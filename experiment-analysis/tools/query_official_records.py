"""Thin read-only query entry point; install the experiment_analysis package."""

if __name__ == '__main__':
    try:
        from experiment_analysis.cli import query_main
    except ModuleNotFoundError as exc:
        if exc.name != 'experiment_analysis':
            raise
        raise SystemExit('Install the local package first: python -m pip install -e ./experiment-analysis') from exc
    query_main()
