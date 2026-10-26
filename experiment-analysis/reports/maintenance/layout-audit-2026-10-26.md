# Experiment Analysis layout audit — 2026-10-26

Reviewed all 68 existing Markdown, HTML, text and TOML documents, including 50 historical documents in handover, legacy-training and maintenance. Read all document text and checked current nonhistorical Markdown relative links; none were broken before changes. This review concerns location, purpose and navigation, not scientific revalidation of historical claims.

## Moves

| Original | Destination | SHA256 (unchanged) |
|---|---|---|
| reports/database/official-records-v1.sqlite | data/database/official-records-v1.sqlite | b86d4a24c1ac1754813ba45c6ae8cf6ae8e38535a56bddc531e2ed5d2ea54d68 |
| tools/templates/database-design/storage-design.md | docs/database/storage-design-template.md | 93fcbdec5d62d879e3eed5ac8aab1ff546199fead32fdedbaa91d30e2d862a81 |

Updated the module README, template lookup in the preparation tool, local ignore rule, current verification report, learning note and learning index. Added docs/README.md to define directory responsibilities. No raw data, extraction reports or dated design snapshots were overwritten. Historical handover paths remain unchanged as evidence. No commit or push was requested for this adjustment.

## Existing document disposition

| Document | Decision |
|---|---|
| pyproject.toml | Keep in current role |
| README.md | Keep; update current paths/status |
| local-work-notes/README.md | Keep; update current paths/status |
| local-work-notes/legacy-training/MISSION.md | Preserve historical evidence |
| local-work-notes/legacy-training/NOTES.md | Preserve historical evidence |
| local-work-notes/legacy-training/RESOURCES.md | Preserve historical evidence |
| local-work-notes/maintenance/2026-10-24-group-training.md | Preserve historical evidence |
| local-work-notes/maintenance/2026-10-24-reorganization.md | Preserve historical evidence |
| local-work-notes/maintenance/approved-organization-ZH-DE.md | Preserve historical evidence |
| local-work-notes/steps/01-experiment-inventory.html | Keep in current role |
| local-work-notes/steps/01-experiment-inventory.md | Keep in current role |
| local-work-notes/steps/02-official-yolo-records.md | Keep in current role |
| local-work-notes/steps/03-second-official-model.md | Keep in current role |
| local-work-notes/steps/04-performance-summary.md | Keep in current role |
| local-work-notes/steps/05-database-design.md | Keep in current role |
| local-work-notes/steps/06-sqlite-import.md | Keep; update current paths/status |
| local-work-notes/handover/2026-10-26/01-项目完整交接.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/02-技术状态与下一步.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/03-新对话开场提示词.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/git-head.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/git-log.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/git-remotes.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/git-status.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/ignore-rule.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/module-file-index.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/evidence/verification.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/requirements.txt | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/START_HERE.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/docs/organization-validation.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/local-work-notes/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/local-work-notes/steps/01-experiment-inventory.html | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/local-work-notes/steps/01-experiment-inventory.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/local-work-notes/steps/02-official-yolo-records.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/local-work-notes/steps/03-second-official-model.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/local-work-notes/steps/04-performance-summary.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/reports/official/comparison-n-s-v8.4.0/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/reports/official/performance-n-s-2026-10-24/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/reports/official/yolo26n-v8.4.0/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/experiment-analysis/reports/official/yolo26s-v8.4.0/README.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/binary_to_multiclass_architecture_validation.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/demo_video_recording_and_inference_summary.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/experiment-01-yolo11m-multiclass-synthetic-validation.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/experiment-02-yolo11m-real-test-evaluation.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_binary_optimization.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_final_experiment_summary.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_multiclass_finetuning_analysis.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_multiclass_real_test_analysis.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_multiclass_training_summary.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_real_test_extra_exploration.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolo11_resolution_and_training_strategy.md | Preserve historical evidence |
| local-work-notes/handover/2026-10-26/snapshot/reports/experiments/yolov8_multiclass_size_effect.md | Preserve historical evidence |
| local-work-notes/legacy-training/learning-records/0001-hardware-constrained-baseline.md | Preserve historical evidence |
| local-work-notes/legacy-training/learning-records/0002-transient-free-vram-is-not-capacity.md | Preserve historical evidence |
| local-work-notes/legacy-training/learning-records/0003-yolo11m-selected-for-formal-training.md | Preserve historical evidence |
| local-work-notes/legacy-training/learning-records/0004-align-yolo11m-with-previous-training.md | Preserve historical evidence |
| local-work-notes/legacy-training/lessons/0001-yolo11-multiclass-training-flow.html | Preserve historical evidence |
| local-work-notes/legacy-training/reference/yolo11-reproducible-training-checklist.html | Preserve historical evidence |
| reports/database/import-verification-2026-10-26.md | Keep; update current paths/status |
| reports/database-design/2026-10-26/mapping-verification.md | Keep in current role |
| reports/database-design/2026-10-26/storage-design.md | Keep in current role |
| reports/official/comparison-n-s-v8.4.0/README.md | Keep in current role |
| reports/official/performance-n-s-2026-10-24/README.md | Keep in current role |
| reports/official/yolo26n-v8.4.0/README.md | Keep in current role |
| reports/official/yolo26s-v8.4.0/README.md | Keep in current role |
| tools/templates/database-design/storage-design.md | Move authored template to docs/database |

## Post-adjustment verification

All 34 tests passed. The preparation tool generated 385 field entries and 34 mappings using the relocated template. Current nonhistorical Markdown local links resolve. The moved database SHA256 is unchanged, SQLite integrity_check returned ok and all 34 measurements remain present. Database and personal notes are ignored by Git. git diff --check passed.
