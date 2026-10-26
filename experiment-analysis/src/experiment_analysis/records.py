"""Read a fixed N/S evidence bundle once; validate before any database write."""
import csv
import hashlib
import io
import json
import math
from datetime import date, datetime
from pathlib import Path

PINS = {
    'YOLO26n': ('yolo26n.pt', 340096055, 5544453, '9b09cc8bf347f0fc8a5f7657480587f25db09b34bf33b0652110fb03a8ad4fef'),
    'YOLO26s': ('yolo26s.pt', 340096060, 20422725, '646f8bc3fe0a656803d95c294f7852321748cb29d13466a1af8862e2db384a1b'),
}
SAVED = {
    'metrics/precision(B)': ('precision', 'ratio'),
    'metrics/recall(B)': ('recall', 'ratio'),
    'metrics/mAP50(B)': ('map50', 'ratio'),
    'metrics/mAP50-95(B)': ('map50_95', 'ratio'),
    'metrics/mAP_small(B)': ('map_small', 'ratio'),
    'metrics/mAP_medium(B)': ('map_medium', 'ratio'),
    'metrics/mAP_large(B)': ('map_large', 'ratio'),
    'val/box_loss': ('box_loss', 'publisher_defined'),
    'val/cls_loss': ('cls_loss', 'publisher_defined'),
    'val/dfl_loss': ('dfl_loss', 'publisher_defined'),
    'fitness': ('fitness', 'publisher_defined'),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, unit):
    require(type(value) in (int, float) and math.isfinite(value), 'Expected finite numeric value')
    require(value >= 0, 'Negative metric')
    if unit in ('ratio', 'percent'):
        require(value <= (1 if unit == 'ratio' else 100), 'Metric outside unit range')
    if unit in ('ms', 'million_parameters', 'billion_operations'):
        require(value > 0, 'Metric must be positive')
    return value


def load_bundle(module_root):
    root = Path(module_root).resolve()
    evidence = {}

    def read(relative):
        raw = (root / relative).read_bytes()
        text = raw.decode('utf-8-sig')
        evidence[relative] = {'path': relative, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        return text

    def document(relative):
        text = read(relative)
        def reject_constant(value):
            raise ValueError(f'Non-finite JSON constant: {value}')
        def unique_keys(pairs):
            result = {}
            for key, value in pairs:
                require(key not in result, f'Duplicate JSON key: {key}')
                result[key] = value
            return result
        obj = json.loads(text, parse_constant=reject_constant, object_pairs_hook=unique_keys)
        canonical(obj)
        return obj, text

    reference_path = 'data/reference/yolo26-official-benchmark-2026-10-24.json'
    ref, ref_text = document(reference_path)
    require((ref['task'], ref['dataset'], ref['split'], ref['image_size_px']) == ('detect', 'COCO', 'val', 640), 'Unsupported benchmark protocol')
    require(type(ref['image_size_px']) is int, 'Invalid image size')
    require(ref['map_unit'] == 'percentage_points_0_to_100', 'Unsupported mAP unit')
    require(ref['latency_head'] == 'one-to-one NMS-free (nms=False)', 'Unsupported latency detection mode')
    require((ref['cpu_backend'], ref['gpu_backend'], ref['gpu_hardware']) == ('ONNX', 'TensorRT10', 'NVIDIA T4'), 'Unsupported timing backend')
    date.fromisoformat(ref['accessed_date'])
    require(ref['source_url'] == 'https://docs.ultralytics.com/models/yolo26/', 'Unexpected benchmark source')
    for key in ('cpu_hardware', 'timing_precision'):
        require(ref[key] is None or (isinstance(ref[key], str) and ref[key]), f'Invalid {key}')
    batch = ref['timing_batch_size']
    require(batch is None or (type(batch) is int and batch > 0), 'Invalid timing batch')
    require([row['model'] for row in ref['models']] == list(PINS), 'Expected unique N/S models in order')
    csv_path = 'reports/official/performance-n-s-2026-10-24/performance_summary.csv'
    reader = csv.DictReader(io.StringIO(read(csv_path)))
    fields = reader.fieldnames
    require(fields and len(fields) == len(set(fields)), 'Duplicate/missing CSV headers')
    csv_rows = list(reader)
    require(len(csv_rows) == 2, 'Expected two CSV rows')
    sources, conditions, measurements, configs = [], [], [], []

    def source(kind, paths, url, observed, raw, metadata=None, asset_hash=None, release=None):
        manifest = sorted((evidence[p] for p in paths), key=lambda entry: entry['path'])
        identity = {'source_kind': kind, 'files': [{'path': p['path'], 'sha256': p['sha256']} for p in manifest]}
        entry = dict(source_kind=kind, source_key=digest(identity), source_url=url,
                     observed_date=observed, release_tag=release, asset_sha256=asset_hash,
                     evidence_json=raw, metadata_json=metadata, input_manifest_json=canonical(manifest))
        sources.append(entry)
        return entry['source_key']

    published = source('published_transcription', [reference_path], ref['source_url'], ref['accessed_date'], ref_text)

    def condition(source_key, purpose, mode, **extra):
        semantic = dict(purpose=purpose, task='detect', dataset=None, split=None,
                        image_size_px=640, detection_mode=mode, backend=None, hardware=None,
                        batch_size=None, precision=None, scope='', evidence_status='publisher_reported', notes='')
        semantic.update(extra)
        key = digest(semantic)
        conditions.append(dict(source_key=source_key, condition_key=key, **semantic))
        return source_key, key

    standard = condition(published, 'accuracy', 'standard', dataset='COCO', split='val', scope='one-to-many + NMS')
    e2e = condition(published, 'accuracy', 'end_to_end', dataset='COCO', split='val', scope=ref['latency_head'])
    cpu = condition(published, 'latency', 'end_to_end', backend='ONNX', hardware=ref['cpu_hardware'], batch_size=batch, precision=ref['timing_precision'], scope=ref['timing_scope'])
    gpu = condition(published, 'latency', 'end_to_end', backend='TensorRT10', hardware=ref['gpu_hardware'], batch_size=batch, precision=ref['timing_precision'], scope=ref['timing_scope'])
    complexity = condition(published, 'complexity', 'not_applicable', scope=ref['complexity_scope'])

    def metric(model, cond, field, name, unit, value, spread=None):
        number(value, unit)
        if spread is not None:
            number(spread, 'spread')
        measurements.append(dict(model=model, source_key=cond[0], condition_key=cond[1], metric_name=name,
                                 raw_value=value, unit=unit, raw_field=field, reported_spread=spread,
                                 spread_definition=ref['spread_definition'] if spread is not None else None))

    for published_row, csv_row in zip(ref['models'], csv_rows):
        model = published_row['model']
        directory = f'reports/official/{model.lower()}-v8.4.0'
        paths = [f'{directory}/{name}.json' for name in ('source', 'training_config', 'saved_metrics', 'checkpoint_metadata')]
        (prov, prov_text), (config, _), (saved, _), (meta, meta_text) = [document(path) for path in paths]
        asset, asset_id, size, sha = PINS[model]
        require((prov['asset_name'], prov['asset_id'], prov['size_bytes'], prov['sha256']) == (asset, asset_id, size, sha), 'Checkpoint identity mismatch')
        url = f'https://github.com/ultralytics/assets/releases/download/v8.4.0/{asset}'
        require(prov['release_tag'] == 'v8.4.0' and prov['download_url'] == url and prov['checksum_matches_official_digest'] is True, 'Checkpoint provenance mismatch')
        require(prov['checkpoint_version'] == meta['version'] and prov['checkpoint_git'] == meta['git'], 'Checkpoint metadata mismatch')
        require(config['task'] == 'detect' and type(config['imgsz']) is int and config['imgsz'] == 640, 'Unsupported checkpoint config')
        require(set(saved) == set(SAVED), 'Unexpected saved metric fields')
        require(type(config['epochs']) is int and config['epochs'] > 0, 'Invalid epochs')
        number(config['lr0'], 'ms')
        number(config['mosaic'], 'ratio')
        observed = datetime.fromisoformat(prov['retrieved_at_utc'])
        require(observed.tzinfo is not None, 'Acquisition timestamp needs timezone')
        checkpoint = source('checkpoint', paths, url, observed.date().isoformat(), prov_text, meta_text, sha, 'v8.4.0')
        saved_condition = condition(checkpoint, 'accuracy', 'unverified', scope='Saved checkpoint metrics; actual evaluation protocol unverified', evidence_status='config_context_only', notes=canonical({'data_config_hint': config['data'], 'split_config_hint': config['split']}))
        configs.append(dict(model=model, source_key=checkpoint, config_json=canonical(config)))
        for field, (name, unit) in SAVED.items():
            metric(model, saved_condition, field, name, unit, saved[field])
        specs = [
            ('map50_95_standard_pct', standard, 'map50_95', 'percent', None),
            ('map50_95_e2e_pct', e2e, 'map50_95', 'percent', None),
            ('cpu_onnx_ms', cpu, 'latency', 'ms', 'cpu_reported_spread_ms'),
            ('t4_tensorrt10_ms', gpu, 'latency', 'ms', 't4_reported_spread_ms'),
            ('params_m', complexity, 'parameters', 'million_parameters', None),
            ('flops_b', complexity, 'flops', 'billion_operations', None),
        ]
        require(set(published_row) == {'model', *(s[0] for s in specs), 'cpu_reported_spread_ms', 't4_reported_spread_ms'}, 'Unexpected published fields')
        for field, cond, name, unit, spread in specs:
            metric(model, cond, field, name, unit, published_row[field], published_row[spread] if spread else None)
        expected = dict(published_row)
        expected.update({key: ref[key] for key in ('task', 'dataset', 'split', 'image_size_px', 'latency_head', 'cpu_hardware', 'gpu_hardware', 'timing_batch_size', 'timing_precision')})
        expected.update(checkpoint_saved_map50_95_ratio=saved['metrics/mAP50-95(B)'],
                        checkpoint_saved_map50_95_pct=round(saved['metrics/mAP50-95(B)'] * 100, 6),
                        checkpoint_saved_head='not_verified_do_not_merge_with_published_modes',
                        checkpoint_coco_epochs=config['epochs'], checkpoint_lr0=config['lr0'], checkpoint_mosaic=config['mosaic'],
                        checkpoint_metrics_file=f'{directory}/saved_metrics.json', checkpoint_sha256=sha,
                        benchmark_source_url=ref['source_url'], benchmark_accessed_date=ref['accessed_date'])
        require(set(csv_row) == set(expected), 'CSV columns differ from expected contract')
        for key, value in expected.items():
            actual = csv_row[key]
            if type(value) in (int, float):
                parsed = float(actual)
                require(math.isfinite(parsed) and abs(parsed - value) <= 1e-9, f'CSV/JSON mismatch: {model}.{key}')
            else:
                require(actual == ('' if value is None else value), f'CSV/JSON mismatch: {model}.{key}')
    return dict(models=list(PINS), sources=sources, conditions=conditions, measurements=measurements,
                configs=configs, validation_csv=evidence[csv_path])
