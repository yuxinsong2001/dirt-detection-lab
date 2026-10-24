"""Compatibility entry point; executing it generates the report, as before."""
from pathlib import Path
from runpy import run_path

globals().update(run_path(
    str(Path(__file__).resolve().parents[1] / "scripts" / "build_abschlussbericht_pdf.py"),
    run_name=__name__,
))
