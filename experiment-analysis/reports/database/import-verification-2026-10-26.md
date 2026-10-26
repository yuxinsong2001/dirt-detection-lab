# SQLite import verification — 2026-10-26

Implemented package modules: records.py, database.py, importing.py and cli.py.
The tools/import_official_records.py wrapper remains a thin entry point.

Current database: data/database/official-records-v1.sqlite (local, ignored).
First import committed 2 models, 3 sources, 7 conditions, 34 measurements and 2 configuration objects containing 226 keys. Repeating the CLI command against this database inserted zero rows into every table. Existing input reports were not regenerated or changed.

Validation: 34 unittest tests passed (24 existing plus 10 database import tests). Database tests verify real fixture population, raw ratio/head separation, NULL timing fields, source traceability, SQLite integrity and foreign keys, same-source repeat, CSV disagreement, invalid numbers, mode/unit rejection, checkpoint identity mismatch, newer dated snapshot coexistence, injected transaction failure including schema rollback, preservation of an existing snapshot on failure, existing value conflict rejection, and refusal to modify an unrelated database.

A SQL acceptance assertion joins accuracy and T4 latency on model, source, detection mode and image size. Only YOLO26s satisfies end-to-end mAP >=45 percent and TensorRT10/T4 latency <=3 ms, returning 47.8 and 2.5. This is an integration test, not a released query command or independent model evaluation.

Runtime dependencies: Python standard library only. Install the package with the same interpreter used for the CLI and tests. Editable installation and tests were run in an isolated verification environment; the user's global environment was not modified.

Limitations: fixed N/S input contract; curves not imported; no schema migrations or user-facing query command yet. A failed first transaction can leave an empty database file, but no committed schema or partial records. The input checks verify extracted source records against pinned provenance, not a fresh download or rehash of PT tensor files. No training, inference, network evaluation, commit or push was performed for this implementation.
Layout correction: the database was originally generated under reports/database and then moved to data/database on 2026-10-26, with unchanged SHA256. This verification report remains under reports/database.
