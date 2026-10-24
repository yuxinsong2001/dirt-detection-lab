"""Compatibility entry point; use scripts/visualize_multiclass_labels.py."""
from pathlib import Path
from runpy import run_path

globals().update(run_path(
    str(Path(__file__).resolve().parents[1] / "scripts" / "visualize_multiclass_labels.py"),
    run_name=__name__,
))
