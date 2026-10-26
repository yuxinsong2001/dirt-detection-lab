"""Thin argument parsing for the reusable importer."""
import argparse
import json
import sqlite3
from pathlib import Path

from . import __version__
from .importing import import_records


def import_main(argv=None):
    parser = argparse.ArgumentParser(description='Validate and atomically import official N/S records into SQLite.')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--module-root', type=Path, required=True, help='Directory containing data/ and reports/')
    parser.add_argument('--database', type=Path, required=True, help='SQLite file; repeated inputs do not add duplicate records')
    args = parser.parse_args(argv)
    try:
        result = import_records(args.module_root, args.database)
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        parser.exit(1, f'Import failed: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


def query_main(argv=None):
    from .queries import filter_models, list_models, model_details

    parser = argparse.ArgumentParser(description='Read-only model inspection and source-aware selection.')
    parser.add_argument('--version', action='version', version=__version__)
    parser.add_argument('--database', type=Path, required=True)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='List model identities and record counts')
    detail = commands.add_parser('show', help='Show raw metrics, conditions, sources and checkpoint configs')
    detail.add_argument('model', help='Exact model name, e.g. YOLO26s')
    select = commands.add_parser('filter', help='Filter compatible published accuracy and latency')
    select.add_argument('--min-map', type=float, required=True, help='mAP50-95 lower bound, percent (0..100)')
    select.add_argument('--max-latency-ms', type=float, required=True)
    select.add_argument('--device', choices=('t4', 'cpu'), default='t4')
    select.add_argument('--mode', choices=('end_to_end', 'standard'), default='end_to_end')
    select.add_argument('--source-date', help='Optional exact source date YYYY-MM-DD; default returns all matching snapshots')
    select.add_argument('--source-key', help='Optional exact source fingerprint from list/show/filter output')
    args = parser.parse_args(argv)
    try:
        if args.command == 'list':
            result = list_models(args.database)
        elif args.command == 'show':
            result = model_details(args.database, args.model)
        else:
            result = filter_models(args.database, min_map=args.min_map, max_latency_ms=args.max_latency_ms,
                                   device=args.device, mode=args.mode, source_date=args.source_date, source_key=args.source_key)
    except (OSError, ValueError, TypeError, sqlite3.Error) as exc:
        parser.exit(1, f'Query failed: {exc}\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
