"""Compare saved N/S configurations descriptively; do not rank models or infer causes."""

import argparse
import csv
import json
import os
from collections import Counter
from pathlib import Path

MODULE_ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = MODULE_ROOT / "reports" / "official"
MISSING = object()


def display(value):
    return "<missing>" if value is MISSING else json.dumps(value, ensure_ascii=False, sort_keys=True)


def compare_dicts(left, right, section="training_config"):
    rows = []
    for key in sorted(set(left) | set(right)):
        a, b = left.get(key, MISSING), right.get(key, MISSING)
        status = ("missing_n" if a is MISSING else "missing_s" if b is MISSING
                  else "same" if display(a) == display(b) else "different")
        rows.append({"section": section, "field": key, "YOLO26n": display(a), "YOLO26s": display(b), "status": status})
    return rows


def read_json(directory, name):
    return json.loads((directory / name).read_text(encoding="utf-8"))


def run(n_dir, s_dir, output):
    if output.exists():
        raise FileExistsError("Comparison output exists; choose a new directory")
    n_config = read_json(n_dir, "training_config.json")
    s_config = read_json(s_dir, "training_config.json")
    n_meta = read_json(n_dir, "checkpoint_metadata.json")
    s_meta = read_json(s_dir, "checkpoint_metadata.json")
    rows = compare_dicts(n_config, s_config)
    rows += compare_dicts(
        {"version": n_meta.get("version"), "git.commit": (n_meta.get("git") or {}).get("commit")},
        {"version": s_meta.get("version"), "git.commit": (s_meta.get("git") or {}).get("commit")},
        "checkpoint_metadata",
    )
    counts = dict(Counter(row["status"] for row in rows if row["section"] == "training_config"))
    n_summary = read_json(n_dir, "inspection_summary.json")
    s_summary = read_json(s_dir, "inspection_summary.json")
    output.mkdir(parents=True)
    with (output / "config_comparison.csv").open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["section", "field", "YOLO26n", "YOLO26s", "status"])
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Official YOLO26n / YOLO26s configuration comparison", "",
        "Descriptive comparison of saved values only. No model ranking or causal conclusion.", "",
        f"Training fields: {len(set(n_config) | set(s_config))}; counts: {json.dumps(counts)}.",
        f"Saved curve rows: N={n_summary['curve_rows']}, S={s_summary['curve_rows']}.", "",
        "## Selected recorded settings", "",
        "| Field | YOLO26n | YOLO26s |", "|---|---|---|",
    ]
    for key in ("task", "data", "model", "epochs", "imgsz", "batch", "optimizer", "seed", "lr0", "lrf", "mosaic", "mixup", "scale", "device"):
        lines.append(f"| {key} | {display(n_config.get(key, MISSING))} | {display(s_config.get(key, MISSING))} |")
    lines += [
        "", "## Interpretation limits", "",
        "- Matching data paths record the same YAML location, not proof of identical image/annotation bytes.",
        "- Training budgets, starting checkpoints, learning rates and augmentations differ. This is not a one-variable controlled comparison.",
        "- Both report the same library version, but the producing Git commits differ. Do not assume identical training/evaluation code.",
        "- Device values such as 3 and 5 are device indices, not GPU model names. They do not establish comparable hardware or speed.",
        "- These are saved training settings. Null or automatic values do not prove a resolved evaluation setting; for example, conf=null is not a known confidence threshold.",
        "- Keep saved checkpoint metrics separate from the final curve row. Do not choose a best epoch by guessing.",
        "- Loss-column names alone do not guarantee the same loss formula across code revisions.",
        "- No accuracy or latency ranking is generated. Later comparisons need an explicit protocol and evidence for missing conditions.",
        "", "## Inputs", "",
        f"- [N configuration]({Path(os.path.relpath(n_dir / 'training_config.json', output)).as_posix()})",
        f"- [S configuration]({Path(os.path.relpath(s_dir / 'training_config.json', output)).as_posix()})",
        "- [All fields and statuses](config_comparison.csv)", "",
        "CSV status values are same, different, missing_n or missing_s. Values retain JSON types; null is distinct from a missing field.",
    ]
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"training_fields": len(set(n_config) | set(s_config)), "training_status_counts": counts, "rows_with_metadata": len(rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n-dir", type=Path, default=OFFICIAL / "yolo26n-v8.4.0")
    parser.add_argument("--s-dir", type=Path, default=OFFICIAL / "yolo26s-v8.4.0")
    parser.add_argument("--output", type=Path, default=OFFICIAL / "comparison-n-s-v8.4.0")
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.n_dir.resolve(), args.s_dir.resolve(), args.output.resolve()), indent=2))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Configuration comparison failed: {exc}\n")


if __name__ == "__main__":
    main()
