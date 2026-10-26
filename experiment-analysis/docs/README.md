# Documentation and directory responsibilities

| Directory | Responsibility |
|---|---|
| src/experiment_analysis/ | Reusable Python implementation |
| tools/ | Command entry points and existing standalone tools |
| tests/ | Automated software checks |
| data/reference/ | Dated official benchmark input transcription |
| data/external/ | Downloaded checkpoint cache, local only |
| data/database/ | SQLite storage and sidecar files, local only |
| docs/ | Maintained design documents and authoring templates |
| reports/ | Generated summaries, extracted evidence and verification reports |
| local-work-notes/ | Personal lessons, interview practice and historical handovers, ignored |

## Design and implementation

[Storage design template](database/storage-design-template.md) is the manually
authored planning document copied into reports by prepare_database_design.py.
Its design-stage status is intentional; it is not a claim about current code.
The dated design under reports/database-design is an output snapshot and remains
unchanged. Current implementation and commands are documented in the
[module README](../README.md) and verified by
[the import report](../reports/database/import-verification-2026-10-26.md).

Extracted N/S JSON/CSV remain under reports/official: they are extraction outputs
with provenance even though the database importer consumes them as inputs.
Reference transcriptions, raw checkpoints and the live SQLite database belong
under data. Report-local READMEs describe the adjacent output files.

Historical handover snapshots preserve the original paths and content. Archived
maintenance scripts under personal notes are historical evidence, not active
tools. Generated Python caches and package metadata are ignored build artifacts.
