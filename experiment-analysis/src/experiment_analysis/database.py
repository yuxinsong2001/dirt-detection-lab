"""Versioned SQLite schema; transaction ownership belongs to the importer."""
import sqlite3

APPLICATION_ID = 0x444E4554
TABLES = ('models', 'sources', 'evaluation_conditions', 'measurements', 'training_configs')
SCHEMA = [
    """CREATE TABLE models (
    id INTEGER PRIMARY KEY, publisher TEXT NOT NULL, family TEXT NOT NULL,
    name TEXT NOT NULL, task TEXT NOT NULL, UNIQUE(publisher,name,task))""",
    """CREATE TABLE sources (
    id INTEGER PRIMARY KEY, source_kind TEXT NOT NULL CHECK(source_kind IN ('published_transcription','checkpoint')),
    source_key TEXT NOT NULL UNIQUE, source_url TEXT NOT NULL, observed_date TEXT,
    release_tag TEXT, asset_sha256 TEXT, evidence_json TEXT NOT NULL, metadata_json TEXT,
    input_manifest_json TEXT NOT NULL, imported_at_utc TEXT NOT NULL)""",
    """CREATE TABLE evaluation_conditions (
    id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL REFERENCES sources(id), condition_key TEXT NOT NULL,
    purpose TEXT NOT NULL CHECK(purpose IN ('accuracy','latency','complexity')), task TEXT NOT NULL,
    dataset TEXT, split TEXT, image_size_px INTEGER CHECK(image_size_px>0),
    detection_mode TEXT NOT NULL CHECK(detection_mode IN ('standard','end_to_end','unverified','not_applicable')),
    backend TEXT, hardware TEXT, batch_size INTEGER CHECK(batch_size>0), precision TEXT,
    scope TEXT NOT NULL, evidence_status TEXT NOT NULL, notes TEXT NOT NULL,
    UNIQUE(source_id,condition_key))""",
    """CREATE TABLE measurements (
    id INTEGER PRIMARY KEY, model_id INTEGER NOT NULL REFERENCES models(id),
    condition_id INTEGER NOT NULL REFERENCES evaluation_conditions(id),
    metric_name TEXT NOT NULL, raw_value REAL NOT NULL CHECK(raw_value>=0 AND raw_value<=1.7976931348623157e308),
    unit TEXT NOT NULL, raw_field TEXT NOT NULL,
    reported_spread REAL CHECK(reported_spread>=0 AND reported_spread<=1.7976931348623157e308), spread_definition TEXT,
    CHECK((unit='ratio' AND raw_value<=1 AND metric_name IN ('precision','recall','map50','map50_95','map_small','map_medium','map_large'))
       OR (unit='percent' AND raw_value<=100 AND metric_name='map50_95')
       OR (unit='ms' AND raw_value>0 AND metric_name='latency')
       OR (unit='million_parameters' AND raw_value>0 AND metric_name='parameters')
       OR (unit='billion_operations' AND raw_value>0 AND metric_name='flops')
       OR (unit='publisher_defined' AND metric_name IN ('box_loss','cls_loss','dfl_loss','fitness'))),
    CHECK(reported_spread IS NULL OR (unit='ms' AND spread_definition IS NOT NULL)),
    UNIQUE(model_id,condition_id,metric_name))""",
    """CREATE TABLE training_configs (
    id INTEGER PRIMARY KEY, model_id INTEGER NOT NULL REFERENCES models(id),
    source_id INTEGER NOT NULL REFERENCES sources(id), config_json TEXT NOT NULL,
    UNIQUE(model_id,source_id))""",
]


def connect(path):
    connection = sqlite3.connect(path, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys=ON')
    return connection


def initialize(connection):
    """Run inside BEGIN; never accept unrelated or future-schema databases."""
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    app = connection.execute('PRAGMA application_id').fetchone()[0]
    version = connection.execute('PRAGMA user_version').fetchone()[0]
    if tables or app or version:
        if app != APPLICATION_ID or version != 1 or tables != set(TABLES):
            raise ValueError('Unrecognized database or unsupported schema version')
        return
    for statement in SCHEMA:
        connection.execute(statement)
    connection.execute(f'PRAGMA application_id={APPLICATION_ID}')
    connection.execute('PRAGMA user_version=1')


def counts(connection):
    return {name: connection.execute(f'SELECT COUNT(*) FROM {name}').fetchone()[0] for name in TABLES}
