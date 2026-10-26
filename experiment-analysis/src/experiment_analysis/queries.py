"""Read-only model inspection and source-aware performance selection."""
import json
import math
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from .database import APPLICATION_ID, TABLES


@contextmanager
def open_readonly(database):
    path = Path(database).resolve()
    if not path.is_file():
        raise ValueError(f'Database file does not exist: {path}')
    connection = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        connection.execute('PRAGMA query_only=ON')
        connection.execute('BEGIN')
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if (connection.execute('PRAGMA application_id').fetchone()[0] != APPLICATION_ID
                or connection.execute('PRAGMA user_version').fetchone()[0] != 1
                or tables != set(TABLES)):
            raise ValueError('Unrecognized database or unsupported schema version')
        yield connection
    finally:
        if connection.in_transaction:
            connection.rollback()
        connection.close()


def list_models(database):
    with open_readonly(database) as connection:
        rows = connection.execute('''SELECT model.name, model.publisher, model.family, model.task,
            COUNT(DISTINCT s.id) AS source_count, COUNT(m.id) AS measurement_count
            FROM models model LEFT JOIN measurements m ON m.model_id=model.id
            LEFT JOIN evaluation_conditions c ON c.id=m.condition_id
            LEFT JOIN sources s ON s.id=c.source_id
            GROUP BY model.id ORDER BY model.name''').fetchall()
        return [dict(row) for row in rows]


def model_details(database, model):
    with open_readonly(database) as connection:
        identity = connection.execute('SELECT id,name,publisher,family,task FROM models WHERE name=?', (model,)).fetchall()
        if not identity:
            raise ValueError(f'Model not found: {model}')
        if len(identity) != 1:
            raise ValueError('Ambiguous model name; database contains multiple identities')
        identity = dict(identity[0])
        model_id = identity.pop('id')
        metrics = connection.execute('''SELECT m.metric_name,m.raw_value,m.unit,m.raw_field,
            m.reported_spread,m.spread_definition,c.purpose,c.task,c.dataset,c.split,c.image_size_px,
            c.detection_mode,c.backend,c.hardware,c.batch_size,c.precision,c.scope,c.evidence_status,c.notes,
            s.source_key,s.source_kind,s.source_url,s.observed_date
            FROM measurements m JOIN evaluation_conditions c ON c.id=m.condition_id
            JOIN sources s ON s.id=c.source_id WHERE m.model_id=?
            ORDER BY s.observed_date,s.source_key,c.purpose,c.detection_mode,m.metric_name''', (model_id,)).fetchall()
        configs = connection.execute('''SELECT s.source_key,s.source_kind,s.source_url,s.observed_date,t.config_json
            FROM training_configs t JOIN sources s ON s.id=t.source_id
            WHERE t.model_id=? ORDER BY s.observed_date,s.source_key''', (model_id,)).fetchall()
        sources = connection.execute('''SELECT s.source_key,s.source_kind,s.source_url,s.observed_date,
            s.release_tag,s.asset_sha256,s.evidence_json,s.metadata_json,s.input_manifest_json,s.imported_at_utc
            FROM sources s WHERE s.id IN (
                SELECT c.source_id FROM measurements m JOIN evaluation_conditions c ON c.id=m.condition_id WHERE m.model_id=?
                UNION SELECT source_id FROM training_configs WHERE model_id=?)
            ORDER BY s.observed_date,s.source_key''', (model_id, model_id)).fetchall()
        return dict(model=identity, measurements=[dict(row) for row in metrics],
                    training_configs=[{**{k: row[k] for k in row.keys() if k != 'config_json'}, 'config': json.loads(row['config_json'])} for row in configs],
                    sources=[{**{k: row[k] for k in row.keys() if k not in ('evidence_json','metadata_json','input_manifest_json')},
                              'evidence': json.loads(row['evidence_json']),
                              'metadata': json.loads(row['metadata_json']) if row['metadata_json'] else None,
                              'input_manifest': json.loads(row['input_manifest_json'])} for row in sources])


def filter_models(database, *, min_map, max_latency_ms, device='t4', mode='end_to_end',
                  source_date=None, source_key=None):
    if type(min_map) not in (int, float) or not math.isfinite(min_map) or not 0 <= min_map <= 100:
        raise ValueError('min_map must be a finite percentage between 0 and 100')
    if type(max_latency_ms) not in (int, float) or not math.isfinite(max_latency_ms) or max_latency_ms <= 0:
        raise ValueError('max_latency_ms must be a finite positive number')
    if device not in ('t4', 'cpu') or mode not in ('end_to_end', 'standard'):
        raise ValueError('Unsupported device or detection mode')
    if source_date is not None:
        if date.fromisoformat(source_date).isoformat() != source_date:
            raise ValueError('source_date must use YYYY-MM-DD')
    backend, hardware = ('TensorRT10', 'NVIDIA T4') if device == 't4' else ('ONNX', None)
    sql = '''SELECT model.name AS model, a.raw_value AS map50_95_pct,l.raw_value AS latency_ms,
        l.reported_spread AS latency_reported_spread_ms,l.spread_definition,
        s.source_key,s.source_url,s.observed_date AS source_date,
        ac.dataset,ac.split,ac.image_size_px,ac.detection_mode,
        lc.backend,lc.hardware,lc.batch_size,lc.precision,lc.scope AS timing_scope,
        lc.evidence_status AS timing_evidence_status
        FROM measurements a JOIN models model ON model.id=a.model_id
        JOIN evaluation_conditions ac ON ac.id=a.condition_id
        JOIN sources s ON s.id=ac.source_id
        JOIN measurements l ON l.model_id=a.model_id
        JOIN evaluation_conditions lc ON lc.id=l.condition_id
            AND lc.source_id=ac.source_id AND lc.task=ac.task
            AND lc.detection_mode=ac.detection_mode AND lc.image_size_px=ac.image_size_px
        WHERE s.source_kind='published_transcription' AND ac.purpose='accuracy'
            AND ac.task='detect' AND ac.dataset='COCO' AND ac.split='val' AND ac.image_size_px=640
            AND ac.evidence_status='publisher_reported' AND lc.evidence_status='publisher_reported'
            AND a.metric_name='map50_95' AND a.unit='percent'
            AND lc.purpose='latency' AND l.metric_name='latency' AND l.unit='ms'
            AND ac.detection_mode=? AND lc.backend=?
            AND a.raw_value>=? AND l.raw_value<=?'''
    params = [mode, backend, min_map, max_latency_ms]
    if device == 't4':
        sql += ' AND lc.hardware=?'
        params.append(hardware)
    # CPU model is unknown in the current input; expose it, never guess a device.
    for column, value in (('s.observed_date', source_date), ('s.source_key', source_key)):
        if value is not None:
            sql += f' AND {column}=?'
            params.append(value)
    sql += ' ORDER BY a.raw_value DESC,l.raw_value,model.name,s.observed_date,s.source_key'
    with open_readonly(database) as connection:
        rows = [dict(row) for row in connection.execute(sql, params)]
    for row in rows:
        row['unknown_conditions'] = [key for key in ('hardware', 'batch_size', 'precision') if row[key] is None]
        row['comparison_note'] = 'Publisher-reported values; unknown timing conditions remain unknown. Not a local performance guarantee.'
    return rows
