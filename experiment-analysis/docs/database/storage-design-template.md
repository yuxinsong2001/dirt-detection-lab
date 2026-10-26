# SQLite storage design — step 1

Status: design only, 2026-10-26. No database, importer, executable schema, or SQL query implementation has been created. This document describes intended behavior, not completed features.

## Inputs and authority

Authoritative published values: data/reference/yolo26-official-benchmark-2026-10-24.json. Authoritative checkpoint values: each N/S source.json, training_config.json, saved_metrics.json and checkpoint_metadata.json. The existing performance_summary.csv is a derived cross-check, not an additional independent source. Reject disagreement rather than silently choosing one value. Check numeric CSV columns against parsed JSON with an explicit tolerance of 1e-9; model names, hashes and source dates must match exactly. Empty CSV condition fields map to JSON null.

The webpage is not archived HTML: the local transcription and its hash establish the saved local evidence, not the complete historical webpage. Preserve collection_method and all source notes. Epoch curves remain in their existing CSV files outside first-version import scope; no raw files are removed.

## Five proposed tables

All integer id fields are primary keys (unique row identifiers). Foreign keys below must be enabled on every SQLite connection with PRAGMA foreign_keys=ON. Fields are required unless marked nullable.

### models

id INTEGER; publisher TEXT; family TEXT; name TEXT; task TEXT. UNIQUE(publisher, name, task). The identity is the published model family/variant, not a particular set of weight bytes. Do not use a training config's model path as the published model name. Seed records: Ultralytics / YOLO26 / YOLO26n or YOLO26s / detect.

### sources

id INTEGER; source_kind TEXT (published_transcription or checkpoint); source_key TEXT UNIQUE; source_url TEXT; observed_date TEXT nullable; release_tag TEXT nullable; asset_sha256 TEXT nullable; evidence_json TEXT; metadata_json TEXT nullable; input_manifest_json TEXT; imported_at_utc TEXT.

Each input manifest entry contains repository-relative path, byte length and SHA256. source_key is SHA256 of canonical JSON containing source_kind and the sorted list of input paths and SHA256 values; use UTF-8, sorted object keys and compact JSON separators. Import time is excluded from identity. The published source contains the reference JSON; each checkpoint source contains its four authoritative JSON files. performance CSV is a validation input recorded in an import report, not source identity. With this design a moved input path is a new source identity; this is a documented first-version tradeoff.

Store original source JSON verbatim as evidence_json and checkpoint metadata JSON as metadata_json; the manifest preserves byte identity. For checkpoints observed_date comes from retrieved_at_utc; retain the complete original timestamp in evidence_json. For the webpage use accessed_date. asset_sha256 identifies checkpoint bytes; the source_key identifies the extracted evidence bundle. New evidence creates a new source, even if it describes the same model. Never silently overwrite historical sources.

### evaluation_conditions

id INTEGER; source_id INTEGER FK sources; condition_key TEXT; purpose TEXT (accuracy, latency, complexity); task TEXT; dataset TEXT nullable; split TEXT nullable; image_size_px INTEGER nullable; detection_mode TEXT (standard, end_to_end, unverified, not_applicable); backend TEXT nullable; hardware TEXT nullable; batch_size INTEGER nullable; precision TEXT nullable; scope TEXT; evidence_status TEXT; notes TEXT. UNIQUE(source_id, condition_key).

condition_key is SHA256 of canonical JSON of all semantic fields after source_id and condition_key; preserve null distinctly from strings. Never use a UNIQUE constraint over nullable semantic columns alone: SQLite permits multiple NULLs. Unknown batch/precision/hardware remain NULL. Dimensions must be positive integers when known, bool is not an integer input. Conditions are source-specific even when displayed values happen to match.

Published accuracy: two conditions, standard and end_to_end, COCO/val/640. Published latency: two conditions, end_to_end/ONNX/unknown CPU and end_to_end/TensorRT10/NVIDIA T4. Input 640 is stated; leave timing dataset and split NULL because the transcription does not establish the timing workload. Published complexity: one condition, task detect, 640, mode not_applicable; retain fused/deployment complexity_scope, unknown hardware. Do not label complexity as a measured runtime.

Checkpoint accuracy: one condition per checkpoint source; task detect and image size 640 are recorded configuration context, head unverified. Dataset and split stay NULL for saved evaluation identity: a saved training data path and split setting do not independently establish the metric's actual evaluation dataset bytes/protocol. notes preserve the COCO config-path hint and split setting; evidence_status=config_context_only. A true end2end training flag does not establish the saved metric head.

### measurements

id INTEGER; model_id INTEGER FK models; condition_id INTEGER FK evaluation_conditions; metric_name TEXT; raw_value REAL; unit TEXT; raw_field TEXT; reported_spread REAL nullable; spread_definition TEXT nullable. UNIQUE(model_id, condition_id, metric_name).

Source is reached through condition_id, avoiding a second potentially contradictory source link. metric_name is a controlled name, unit is validated against that name. Published map50_95 uses percent (0..100); checkpoint precision/recall/AP fields use ratio (0..1). Preserve checkpoint raw_value and raw_field; percent conversion is a query expression, not a second independent observation. Latency uses ms and must be >0; params use million_parameters and FLOPs use billion_operations, both >0. Loss and fitness use publisher_defined, finite and >=0; do not assert fitness is an AP score. Preserve the full 11 saved keys per checkpoint, including losses and fitness. Published reported spread goes on the corresponding latency measurement, finite and >=0; its statistic remains unspecified, not a confidence interval. Reject bool, NaN and infinity before binding values. Unknown required metric values are rejected; unknown optional conditions remain NULL. Proposed CHECK constraints enforce ranges, importer rules enforce cross-table metric/purpose compatibility.

### training_configs

id INTEGER; model_id INTEGER FK models; source_id INTEGER FK sources; config_json TEXT. UNIQUE(model_id, source_id). Store one JSON object per checkpoint with all 113 keys and original JSON types, including explicit null. Missing key differs from an explicit null. First-version queries target performance, so 113 parameter rows or columns are unnecessary. Later parameter search may use SQLite JSON functions after runtime capability checks, or a separate parameter table. Only checkpoint sources are allowed here; enforce this during import. No training recipe is attributed to webpage scores.

## Import and query contract for the next step

Validate all inputs and CSV agreement first, then create/reuse identities and insert the complete bundle in one transaction. Checkpoint source/hash/asset/model associations must match pinned N/S identity. Duplicate source keys mean no new measurements/configs, not an update. Existing identical keys with conflicting contents are errors. Any failure rolls back the bundle; use parameterized SQL. These are requirements, not tested implementation guarantees yet.

Selection must join accuracy and latency on model AND published source AND compatible image size and detection mode, with explicit metric/purpose/backend filters. Do not join on model name alone. CPU and GPU latency are separate conditions. Return missing timing batch and precision and comparison limitations, not an unconditional performance promise.

Acceptance query: from this dated published source select end_to_end map50_95 >=45 percent and NVIDIA T4 / TensorRT10 latency <=3 ms. Expected result: YOLO26s, 47.8 percent and 2.5 ms. YOLO26n fails accuracy at 40.1. Unknown timing details must be displayed. Do not compare checkpoint saved AP with this latency.

## Expected initial population

2 model rows; 3 source rows (one transcription, two checkpoints); 7 condition rows (five published plus two checkpoint); 34 measurements (six published metrics per model =12, eleven checkpoint keys per model =22); 2 configuration rows containing 226 total keys. Reported spreads are attributes of latency measurements, not extra measurements. These counts are proposed import acceptance targets; no database has been populated.

## Required verification when implementation begins

Success and traceability; same-bundle repeat leaves counts unchanged; changed snapshot coexists; CSV/JSON disagreement rejected; invalid values/units and incompatible metric modes rejected; unknown timing conditions retained; checkpoint model identity mismatch rejected; injected mid-import failure rolls back all rows; exact query returns only S and cannot combine different dates/modes. Step 1 only checks the input-to-design mapping, not these future SQL behaviors.
