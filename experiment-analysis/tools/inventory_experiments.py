"""Inventory existing experiment records without loading models or modifying inputs."""

import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


ALIASES = {
    "precision": ("metrics/precision(B)", "metrics/precision"),
    "recall": ("metrics/recall(B)", "metrics/recall"),
    "map50": ("metrics/mAP50(B)", "metrics/mAP_0.5"),
    "map50_95": ("metrics/mAP50-95(B)", "metrics/mAP_0.5:0.95"),
}


def inspect_csv(path, root):
    """Report structure and byte-identical copies; do not infer experiment quality."""
    raw = path.read_bytes()
    record = {
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "rows": 0,
        "columns": [],
        "metric_columns": {},
        "config_files": [name for name in ("args.yaml", "opt.yaml", "hyp.yaml")
                         if (path.parent / name).is_file()],
        "issues": [],
    }
    try:
        reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
        headers = reader.fieldnames or []
        clean_headers = [name.strip() for name in headers]
        record["columns"] = clean_headers
        if not headers:
            record["issues"].append("missing_header")
        if len(set(clean_headers)) != len(clean_headers):
            record["issues"].append("duplicate_column_names")
        for row in reader:
            if not any(value not in (None, "") for value in row.values()):
                continue
            record["rows"] += 1
            if None in row or any(value is None for value in row.values()):
                if "inconsistent_row_width" not in record["issues"]:
                    record["issues"].append("inconsistent_row_width")
        for metric, candidates in ALIASES.items():
            match = next((name for name in candidates if name in clean_headers), None)
            if match:
                record["metric_columns"][metric] = match
        if record["rows"] == 0:
            record["issues"].append("no_data_rows")
        if record["rows"] == 1:
            record["issues"].append("single_row_review_purpose")
        if not record["config_files"]:
            record["issues"].append("no_adjacent_config")
        missing = sorted(set(ALIASES) - set(record["metric_columns"]))
        if missing:
            record["issues"].append("missing_metrics:" + ",".join(missing))
    except (UnicodeError, csv.Error) as exc:
        record["issues"].append("csv_read_error:" + str(exc))
    return record


def inventory(root):
    root = Path(root).resolve()
    runs = root / "runs"
    if not runs.is_dir():
        raise ValueError(f"Missing runs directory: {runs}")
    records = [inspect_csv(path, root) for path in sorted(runs.rglob("results.csv"))]
    groups = {}
    for record in records:
        groups.setdefault(record["sha256"], []).append(record["path"])
    other_csvs = [path.relative_to(root).as_posix()
                  for path in sorted(runs.rglob("*.csv")) if path.name != "results.csv"]
    return {
        "schema_version": 1,
        "scope": "runs directory only; file inventory, not independent experiment count",
        "root": root.as_posix(),
        "summary": {
            "training_csv_files": len(records),
            "training_rows_including_copies": sum(item["rows"] for item in records),
            "distinct_csv_byte_contents": len(groups),
            "row_count_distribution": dict(Counter(str(item["rows"]) for item in records)),
            "other_csv_files": len(other_csvs),
        },
        "byte_identical_groups": [paths for paths in groups.values() if len(paths) > 1],
        "training_records": records,
        "other_csv_paths": other_csvs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, help="New JSON file; existing files are never overwritten")
    args = parser.parse_args()
    try:
        report = inventory(args.root)
        payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            # Exclusive creation deliberately refuses to overwrite any existing file.
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
            print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
        else:
            print(payload, end="")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Inventory failed: {exc}\n")


if __name__ == "__main__":
    main()
