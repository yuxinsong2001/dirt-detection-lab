# Original YOLO project utilities

Run from the repository root. The original tools/ commands and root converter
remain compatibility entry points; use scripts/ for new commands.

| Script | Purpose | Writes files? |
|---|---|---|
| configure_dataset.py | Create a machine-local data YAML | Yes; refuses existing output |
| visualize_multiclass_labels.py | Render labelled image previews | Yes; same-named previews may be replaced |
| dataset_convert_to_yolo_binary.py | Convert original source data to binary YOLO labels | Yes; do not run during organization checks; --clear removes converted output |
| build_abschlussbericht_pdf.py | Generate the historical IEEE-style report | Yes; replaces its report output when executed |

```powershell
python scripts/configure_dataset.py --help
python scripts/visualize_multiclass_labels.py --help
python scripts/dataset_convert_to_yolo_binary.py --help
```

The PDF generator requires the optional requirements-reporting.txt dependencies.
Its historical report text is preserved; organization work does not validate or
update the scientific claims inside it. Do not import it just to inspect it:
the existing script generates a PDF at top level.

The new experiment analysis system is separate: see ../experiment-analysis/README.md.
