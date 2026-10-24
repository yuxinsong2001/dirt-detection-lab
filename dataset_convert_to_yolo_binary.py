"""Compatibility entry point; implementation lives in scripts/."""
from pathlib import Path
from runpy import run_path

globals().update(run_path(
    str(Path(__file__).resolve().parent / "scripts" / "dataset_convert_to_yolo_binary.py"),
    run_name=__name__,
))
