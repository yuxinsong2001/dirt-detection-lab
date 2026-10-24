# Repository layout and maintenance policy

## Two related parts

The original project trains and evaluates YOLO dirt/object detectors. Original
utilities live in scripts, dataset configurations in cfg, experimental evidence
in runs, and project reports in reports. The root data converter and tools files
are compatibility launchers, not duplicate implementations.

The new experiment-analysis module remains self-contained: its own tools, tests,
generated reports and local-only bilingual learning notes stay together. It reads
the original runs directory rather than copying experiment records.

## Stable data and environment paths

- data contains the current local images/labels; datasets contains documented
  dataset layouts. They are not interchangeable aliases and were not moved.
- binary_full.yaml and multiclass_small.yaml remain unchanged compatibility
  configurations. Their documented dataset splits are not populated on this machine.
- cfg/local YAMLs point at the existing local data. Use them explicitly for this
  machine; their train/validation/test definitions must still match the experiment.
- Root checkpoints, weights, historical runs and original args.yaml are unchanged.
- ultralytics-repo is a nested Git repository and is actively imported by .venv.
  It must stay put. The separate report worktree is also untouched.

## Output ownership

| Content | Destination |
|---|---|
| Original experiment logs, metrics, plots | runs |
| Original project reports and summaries | reports |
| Original report source and deliverables | reports/sources, reports/pdf, reports/presentations |
| Original utility-generated figures | reports/figures |
| Historical report drafts and previews | reports/archive (local, ignored) |
| New analysis results | experiment-analysis/reports |
| Personal bilingual explanations | experiment-analysis/local-work-notes (local, ignored) |
| Runtime text logs | logs (log files ignored) |
| Source download archives | archive/source-downloads (archives ignored) |

The data converter intentionally writes converted datasets/configurations rather
than reports. Keep dataset and checkpoint names from historical runs unchanged.

## Git policy

Selected run CSV, YAML, PNG and MP4 records are visible to Git even after a move.
Weights, JPEG preview batches and other new runtime outputs remain ignored unless
already tracked. Existing tracked files are unaffected by ignore rules.

The organization workflow did not automatically stage, commit or push files.
The user subsequently authorized five separate local commits; pushing remains a
separate action and has not been requested.
Git may show old paths as deleted and new destinations as untracked until an
explicitly requested commit. Those statuses are not evidence that files were lost.
Do not commit a deletion-only change without checking destinations.

## Validation and limitations

See [the completed validation record](organization-validation.md) for measured
results and checks not performed. Local VS Code workspace settings hide dependency
internals from Explorer only; they do not remove files or alter runtime imports.

Use the six experiment-analysis tests, safe CLI help checks, source syntax checks,
relative-link checks and before/after SHA-256 comparisons. Never test organization
by running dataset conversion, training, --clear, or report regeneration.

ReportLab is an optional dependency for the historical PDF generator and is not
currently installed in this .venv. Full GPU workflows and report regeneration are
not validated by lightweight checks. A byte-identical checkpoint may have a renamed
file; document a verified SHA-256 match rather than guessing or copying weights.
