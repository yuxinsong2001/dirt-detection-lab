"""Atomic imports with immutable evidence and repeat-import conflict checks."""
from datetime import datetime, timezone
from pathlib import Path

from .database import connect, counts, initialize
from .records import load_bundle


def ensure_row(connection, table, identity, values):
    # Table/column names are internal constants, never user supplied.
    where = ' AND '.join(f'{key}=?' for key in identity)
    row = connection.execute(f'SELECT * FROM {table} WHERE {where}', tuple(identity.values())).fetchone()
    if row is not None:
        if any(row[key] != value for key, value in values.items()):
            raise ValueError(f'Existing {table} record conflicts with input; refusing overwrite')
        return row['id']
    data = {**identity, **values}
    columns = ','.join(data)
    placeholders = ','.join('?' for _ in data)
    return connection.execute(f'INSERT INTO {table} ({columns}) VALUES ({placeholders})', tuple(data.values())).lastrowid


def import_records(module_root, database):
    bundle = load_bundle(module_root)  # All file reads/validation precede opening SQLite.
    target = Path(database).resolve()
    root = Path(module_root).resolve()
    if target == root or target.suffix.lower() not in ('.sqlite', '.sqlite3', '.db'):
        raise ValueError('Database destination must have a .sqlite, .sqlite3 or .db suffix')
    # Never overwrite any source file; SQLite also rejects unrelated existing databases.
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(target)
    try:
        connection.execute('BEGIN IMMEDIATE')
        initialize(connection)
        before = counts(connection)
        models = {name: ensure_row(connection, 'models', dict(publisher='Ultralytics', name=name, task='detect'), dict(family='YOLO26')) for name in bundle['models']}
        sources = {}
        for entry in bundle['sources']:
            values = {key: value for key, value in entry.items() if key != 'source_key'}
            old = connection.execute('SELECT imported_at_utc FROM sources WHERE source_key=?', (entry['source_key'],)).fetchone()
            values['imported_at_utc'] = old[0] if old else datetime.now(timezone.utc).isoformat()
            sources[entry['source_key']] = ensure_row(connection, 'sources', dict(source_key=entry['source_key']), values)
        conditions = {}
        for entry in bundle['conditions']:
            identity = dict(source_id=sources[entry['source_key']], condition_key=entry['condition_key'])
            values = {key: value for key, value in entry.items() if key not in ('source_key', 'condition_key')}
            conditions[(entry['source_key'], entry['condition_key'])] = ensure_row(connection, 'evaluation_conditions', identity, values)
        for entry in bundle['measurements']:
            identity = dict(model_id=models[entry['model']], condition_id=conditions[(entry['source_key'], entry['condition_key'])], metric_name=entry['metric_name'])
            values = {key: value for key, value in entry.items() if key not in ('model', 'source_key', 'condition_key', 'metric_name')}
            ensure_row(connection, 'measurements', identity, values)
        for entry in bundle['configs']:
            ensure_row(connection, 'training_configs', dict(model_id=models[entry['model']], source_id=sources[entry['source_key']]), dict(config_json=entry['config_json']))
        after = counts(connection)
        connection.execute('COMMIT')
        return dict(database=str(target), totals=after, inserted={key: after[key] - before[key] for key in after}, validation_csv=bundle['validation_csv'])
    except BaseException:
        if connection.in_transaction:
            connection.execute('ROLLBACK')
        raise
    finally:
        connection.close()
