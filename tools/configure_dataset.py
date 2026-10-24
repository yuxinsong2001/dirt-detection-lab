"""Compatibility entry point; use scripts/configure_dataset.py for new commands."""
from pathlib import Path
from runpy import run_path

globals().update(run_path(
    str(Path(__file__).resolve().parents[1] / "scripts" / "configure_dataset.py"),
    run_name=__name__,
))
