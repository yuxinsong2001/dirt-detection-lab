"""Thin command entry point; install the package before running this file."""

if __name__ == "__main__":
    try:
        from experiment_analysis.cli import import_main
    except ModuleNotFoundError as exc:
        if exc.name != "experiment_analysis":
            raise
        raise SystemExit(
            "Package is not installed. From the repository root run: "
            "python -m pip install -e ./experiment-analysis"
        ) from exc
    import_main()
