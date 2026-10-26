"""Inventory and cross-check existing N/S evidence for the SQLite design.

The storage design is a manually authored template, not inferred by this tool.
No database, network, model execution, or personal learning notes are generated.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def run(module_root, output):
    ROOT = Path(module_root).resolve()
    OUT = Path(output).resolve()
    if OUT.exists():
        raise FileExistsError('Output exists; choose a new directory')
    def load(path):
        return json.loads(path.read_text(encoding='utf-8'))

    reference = ROOT / 'data/reference/yolo26-official-benchmark-2026-10-24.json'
    summary = ROOT / 'reports/official/performance-n-s-2026-10-24/performance_summary.csv'
    ref = load(reference)
    inputs = [reference, summary]
    for model in ('n', 's'):
        inputs.extend(ROOT / f'reports/official/yolo26{model}-v8.4.0/{name}.json'
                      for name in ('source', 'training_config', 'saved_metrics', 'checkpoint_metadata'))
    rows = list(csv.DictReader(io.StringIO(summary.read_text(encoding='utf-8-sig'))))
    require(len(rows) == 2, 'Input mapping check failed: len(rows) == 2')

    def destination(name, path):
        if name == 'training_config.json': return 'training_configs.config_json (preserve original key/type)'
        if name == 'saved_metrics.json': return 'measurements (raw key, value and explicit unit)'
        if name in ('source.json', 'checkpoint_metadata.json'): return 'sources.evidence_json / metadata_json'
        if name.endswith('.csv'): return 'cross-check only; do not import a second copy of authoritative JSON values'
        if path.endswith('.model'): return 'models.name'
        if path.startswith('models['): return 'measurements; model field selects models.name'
        if path in ('task', 'dataset', 'split', 'image_size_px', 'latency_head', 'cpu_backend', 'cpu_hardware', 'gpu_backend', 'gpu_hardware', 'timing_batch_size', 'timing_precision', 'timing_scope', 'complexity_scope'):
            return 'evaluation_conditions (only where applicable)'
        return 'sources.evidence_json'

    inventory = []
    def flatten(value, path=''):
        if isinstance(value, dict) and value:
            for key, child in value.items(): yield from flatten(child, f'{path}.{key}' if path else key)
        elif isinstance(value, list) and value:
            for i, child in enumerate(value): yield from flatten(child, f'{path}[{i}]')
        else: yield path, value
    for source in inputs:
        if source.suffix == '.csv':
            for key in rows[0]:
                values = [r[key] for r in rows]
                inventory.append([source.relative_to(ROOT).as_posix(), key, 'CSV text', any(v == '' for v in values), json.dumps(values, ensure_ascii=False), destination(source.name, key)])
        else:
            for key, value in flatten(load(source)):
                inventory.append([source.relative_to(ROOT).as_posix(), key, type(value).__name__, value is None, json.dumps(value, ensure_ascii=False), destination(source.name, key)])
    buffer = io.StringIO(newline='')
    writer = csv.writer(buffer)
    writer.writerow(['input_file', 'field_path', 'observed_type', 'observed_missing', 'observed_value', 'proposed_destination'])
    writer.writerows(inventory)

    design = (Path(__file__).resolve().parents[1] / 'docs/database/storage-design-template.md').read_text(encoding='utf-8')

    checks = []
    mapping = []
    for row, model in zip(rows, ref['models']):
        require(row['model'] == model['model'], "Input mapping check failed: row['model'] == model['model']")
        for key, value in model.items():
            if key != 'model':
                require(abs(float(row[key]) - value) < 1e-9, f'Published value mismatch: {key}')
        suffix = model['model'][-1]
        directory = ROOT / f'reports/official/yolo26{suffix}-v8.4.0'
        config, metrics, provenance = [load(directory / name) for name in ('training_config.json', 'saved_metrics.json', 'source.json')]
        require(len(config) == 113 and len(metrics) == 11, 'Input mapping check failed: len(config) == 113 and len(metrics) == 11')
        require(row['checkpoint_sha256'] == provenance['sha256'], "Input mapping check failed: row['checkpoint_sha256'] == provenance['sha256']")
        require(float(row['checkpoint_saved_map50_95_ratio']) == metrics['metrics/mAP50-95(B)'], "Input mapping check failed: float(row['checkpoint_saved_map50_95_ratio']) == metrics['metrics/mAP50-95(B)']")
        require(abs(float(row['checkpoint_saved_map50_95_pct']) - 100 * metrics['metrics/mAP50-95(B)']) < 1e-9, "Input mapping check failed: abs(float(row['checkpoint_saved_map50_95_pct']) - 100 * metrics['metrics/mAP50-95(B)']) < 1e-9")
        require(all(row[key] == '' and ref[key] is None for key in ('cpu_hardware', 'timing_batch_size', 'timing_precision')), "Input mapping check failed: all(row[key] == '' and ref[key] is None for key in ('cpu_hardware', 'timing_batch_size', 'timing_precision'))")
        require(row['benchmark_accessed_date'] == ref['accessed_date'] and row['benchmark_source_url'] == ref['source_url'], "Input mapping check failed: row['benchmark_accessed_date'] == ref['accessed_date'] and row['benchmark_source_url'] == ref['source_url']")
        for key in ('epochs', 'lr0', 'mosaic'):
            require(float(row['checkpoint_' + ('coco_epochs' if key == 'epochs' else key)]) == config[key], "Input mapping check failed: float(row['checkpoint_' + ('coco_epochs' if key == 'epochs' else key)]) == config[key]")
        for key, value in model.items():
            if key == 'model' or 'spread' in key: continue
            purpose = 'accuracy' if 'map' in key else 'latency' if key.endswith('_ms') else 'complexity'
            mapping.append(f"| {model['model']} | published transcription | {purpose} | {key} | {value} |")
        for key, value in metrics.items():
            mapping.append(f"| {model['model']} | checkpoint {suffix.upper()} | accuracy / head unverified | {key} | {value} |")
        checks.append(f"- {model['model']}: published numeric values, saved mAP raw/conversion, source hash/date/URL, missing timing fields, selected config values agree; 113 config keys and 11 saved metrics present.")
    require(len(mapping) == 34, 'Input mapping check failed: len(mapping) == 34')
    manifest = [{'path': p.relative_to(ROOT).as_posix(), 'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs]
    verification = '# Step 1 mapping verification\n\nRead-only input checks passed on 2026-10-26. This is not database/import/query validation.\n\n' + '\n'.join(checks) + f'\n- Field inventory contains {len(inventory)} leaf/CSV-column entries across {len(inputs)} files. observed_missing describes current data only, not a future constraint.\n- Expected selection evaluated directly from source JSON: only YOLO26s satisfies e2e mAP >=45 and T4 latency <=3. No SQL executed.\n\n| Model | Source | Purpose | Original field | Value |\n|---|---|---|---|---:|\n' + '\n'.join(mapping) + '\n\n## Input manifest\n\n```json\n' + json.dumps(manifest, indent=2) + '\n```\n'
    require([m['model'] for m in ref['models'] if m['map50_95_e2e_pct'] >= 45 and m['t4_tensorrt10_ms'] <= 3] == ['YOLO26s'], "Input mapping check failed: [m['model'] for m in ref['models'] if m['map50_95_e2e_pct'] >= 45 and m['t4_tensorrt10_ms'] <= 3] == ['YOLO26s']")


    files = {'storage-design.md': design, 'field-inventory.csv': buffer.getvalue(), 'mapping-verification.md': verification}
    OUT.mkdir(parents=True, exist_ok=False)
    for name, content in files.items():
        with (OUT / name).open('x', encoding='utf-8-sig' if name.endswith('.csv') else 'utf-8', newline='') as f: f.write(content)
    print(json.dumps({'files': list(files), 'input_files': len(inputs), 'field_entries': len(inventory), 'mapped_measurements': len(mapping), 'checks': 'passed'}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module-root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.module_root / 'reports/database-design/2026-10-26'
    try:
        run(args.module_root, output)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'Database design preparation failed: {exc}\n')


if __name__ == '__main__':
    main()
