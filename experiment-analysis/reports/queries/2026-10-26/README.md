# Read-only query verification — 2026-10-26

Implemented list_models, model_details and filter_models in the package, a
query CLI dispatcher and thin tools/query_official_records.py entry point.
The package registers dirtnet-query-records. queries.py performs all reads;
there are no duplicated SQL statements in the tools wrapper.

Validation: 47 tests passed (34 previous plus 13 query tests). Tests cover
actual input population and config/source detail, expected selection and NULL
conditions, no matches, CPU/T4 isolation, standard/checkpoint score isolation,
source and date isolation, mode and image size isolation, invalid thresholds,
unknown model and injection strings, missing/unrelated databases, command
dispatch, write rejection and unchanged database bytes.

Three actual CLI commands ran against data/database/official-records-v1.sqlite.
Outputs are models.json, yolo26s-details.json and selection.json. The database
SHA256 was unchanged. Selection returned only YOLO26s, 47.8 percent e2e mAP and
2.5 ms T4 TensorRT10 timing, from the 2026-10-24 source. Batch and precision
remain null. These values are publisher records, not independent evaluation.

No default latest snapshot selection or cross-source combination is performed.
All eligible snapshots remain separate results; explicit source/date filters
are available. Standard-mode joint selection is empty when no standard timing
is present. Only detection/COCO/val/640 published accuracy is supported by the
initial performance selection contract. No interactive page or chart is added.

The initial test run exposed test-fixture connections not explicitly closed on
Windows; tests now close those connections before temporary file cleanup.
Product queries always close their connections in finally blocks.
