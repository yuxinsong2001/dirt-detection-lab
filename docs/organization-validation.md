# Repository organization validation — 2026-10-24

## Scope

Implemented the user-approved structural cleanup. This is a file-organization
change, not a model, data-processing or scientific-method change. No training,
dataset conversion, dependency installation, PDF regeneration, Git staging,
commit or push was performed. No files were deleted.

## Moves and compatibility

- Moved four utility implementations into scripts. Three tools launchers and the
  root converter preserve old entry points, including access to existing functions.
- Adjusted the relocated converter's repository-root calculation; dataset paths
  and conversion behavior are unchanged.
- Grouped ten Markdown summaries into reports/experiments.
- Preserved eight render-preview PNGs and earlier PDF/PPTX/inspection exports in
  reports/archive. Moved four root logs to logs after exclusive-open lock probes.
- Preserved the source ZIP under archive/source-downloads.
- A total of 32 existing files were moved and hash-checked before link edits.
- Kept the experiment-analysis module together and its personal notes local-only.
- Left data, datasets, runs, checkpoints, nested Ultralytics checkout, virtual
  environment and separate report worktree untouched in this approved cleanup.

Detailed local move and evidence manifests are under the ignored
experiment-analysis/local-work-notes/maintenance directory. They are local records,
not a replacement for backups.

## Results

| Check | Result |
|---|---|
| Original analysis unit tests | 6 passed |
| New compatibility tests | 3 passed; includes six old/new CLI help invocations |
| Original evidence/configuration files | 640 hashes checked; no changes |
| Owned Python syntax | 11 files parsed successfully |
| Current Markdown relative links | No missing targets in checked current documents |
| Local HTML links and stylesheets | No missing targets |
| Experiment inventory | 41 CSV files, 858 rows including copies, 39 byte-distinct CSV contents |
| Previously tracked files absent at old paths | All 338 located at new destinations |
| Relocation comparison against HEAD | 333 identical after newline normalization for text; five reports have expected link/path-note edits |
| Grouped run files visible as untracked | 318; no longer hidden by the broad run ignore rule |

Historical personal maintenance records are preserved as historical records rather
than continuously rewritten. Dataset configuration references and checkpoint links
may be valid only locally because datasets and weights are intentionally not uploaded.

## Known limitations

The statements below about an uncommitted working tree describe the organization
audit before the user subsequently authorized five local commits. That separate
commit operation preserves the moved files and does not push to GitHub.

- The shared root data YAMLs target dataset splits not populated in this checkout.
  Existing cfg/local YAMLs resolve to actual local data; choose the correct task and
  data version rather than silently replacing shared configurations.
- Not all historical checkpoints exist. For the multiclass baseline report, the
  renamed best_dirt_multiclass_11m_e30_i1024_b2.pt was verified against the report's
  original SHA-256 before its link was repaired. No weights were copied or invented.
- ReportLab is absent from the current virtual environment. Its optional dependency
  file is provided, but report generation was not executed or validated end-to-end.
- Training/inference behavior on the GPU was not exercised. The original editable
  Ultralytics source location remains unchanged.
- Git still shows old-path removals and new files because no commit was requested.
  Include both sides of moves in any future authorized commit; do not push a
  deletion-only change. Git history and the index are not rewritten by this cleanup.

## VS Code

An ignored .vscode/settings.json hides environment internals, caches and third-party
source directories from Explorer only. It does not move or remove them. To reveal
one, change its files.exclude value to false in workspace settings. The configuration
is machine-local and will not be included by a normal git add.
