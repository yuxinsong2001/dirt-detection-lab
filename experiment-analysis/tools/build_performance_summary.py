"""Join a dated official benchmark transcription with separate checkpoint records.

No network, model loading, training or inference. CSV is pipeline data, not an
Excel workbook. Official published values remain distinct from pinned assets.
"""

import argparse
import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/reference/yolo26-official-benchmark-2026-10-24.json"
OFFICIAL = ROOT / "reports/official"
OUTPUT = OFFICIAL / "performance-n-s-2026-10-24"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_rows(source, official):
    if (source["task"], source["dataset"], source["split"], source["image_size_px"]) != ("detect", "COCO", "val", 640):
        raise ValueError("Unexpected benchmark task, dataset, split or image size")
    models = source["models"]
    if [m["model"] for m in models] != ["YOLO26n", "YOLO26s"]:
        raise ValueError("Expected exactly one N and one S row in N/S order")
    rows = []
    for model in models:
        for key, value in model.items():
            if key != "model" and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
                raise ValueError(f"Invalid numeric benchmark: {key}")
        for key in ("map50_95_standard_pct", "map50_95_e2e_pct"):
            if not 0 <= model[key] <= 100:
                raise ValueError("Published mAP must use the 0..100 scale")
        for key in ("params_m", "flops_b", "cpu_onnx_ms", "t4_tensorrt10_ms"):
            if model[key] <= 0:
                raise ValueError(f"Expected positive benchmark: {key}")
        directory = official / f"{model['model'].lower()}-v8.4.0"
        config = read_json(directory / "training_config.json")
        metrics = read_json(directory / "saved_metrics.json")
        provenance = read_json(directory / "source.json")
        if config["task"] != "detect" or config["imgsz"] != 640:
            raise ValueError("Unexpected checkpoint task or image size")
        saved_map = metrics["metrics/mAP50-95(B)"]
        if type(saved_map) not in (int, float) or not math.isfinite(saved_map) or not 0 <= saved_map <= 1:
            raise ValueError("Checkpoint mAP must use the 0..1 scale")
        rows.append({
            **model,
            "task": source["task"], "dataset": source["dataset"], "split": source["split"],
            "image_size_px": source["image_size_px"], "latency_head": source["latency_head"],
            "cpu_hardware": source["cpu_hardware"], "gpu_hardware": source["gpu_hardware"],
            "timing_batch_size": source["timing_batch_size"], "timing_precision": source["timing_precision"],
            "checkpoint_saved_map50_95_ratio": saved_map,
            "checkpoint_saved_map50_95_pct": round(saved_map * 100, 6),
            "checkpoint_saved_head": "not_verified_do_not_merge_with_published_modes",
            "checkpoint_coco_epochs": config["epochs"], "checkpoint_lr0": config["lr0"],
            "checkpoint_mosaic": config["mosaic"],
            "checkpoint_metrics_file": (directory / "saved_metrics.json").relative_to(ROOT).as_posix(),
            "checkpoint_sha256": provenance["sha256"],
            "benchmark_source_url": source["source_url"], "benchmark_accessed_date": source["accessed_date"],
        })
    return rows


def report(rows, source):
    n, s = rows
    delta = s["map50_95_e2e_pct"] - n["map50_95_e2e_pct"]
    return f"""# 官方 YOLO26n / YOLO26s 性能比较

比较目标：各自经过官方优化后的发布方案，不研究单个训练参数的因果作用。不训练，不重新评估。

## 性能总表

| 模型 | 普通检测 mAP50–95 | 端到端 mAP50–95 | CPU ONNX延迟(ms) | T4 TensorRT10延迟(ms) | 参数量(M) | FLOPs(B) |
|---|---:|---:|---:|---:|---:|---:|
""" + "\n".join(
        f"| {r['model']} | {r['map50_95_standard_pct']} | {r['map50_95_e2e_pct']} | {r['cpu_onnx_ms']} ± {r['cpu_reported_spread_ms']} | {r['t4_tensorrt10_ms']} ± {r['t4_reported_spread_ms']} | {r['params_m']} | {r['flops_b']} |"
        for r in rows
    ) + f"""

mAP采用0–100尺度。M=百万，B=十亿。±是官方表原值，未解释为置信区间。

## 能得出的结论

- 在官方报告的COCO val、640输入下，S的端到端mAP比N高{delta:.1f}个百分点。普通检测的差值也是{s['map50_95_standard_pct'] - n['map50_95_standard_pct']:.1f}个百分点。
- S参数量约为N的{s['params_m'] / n['params_m']:.2f}倍，FLOPs约为{s['flops_b'] / n['flops_b']:.2f}倍。
- 官方表报告S在T4 TensorRT10的延迟为N的{s['t4_tensorrt10_ms'] / n['t4_tensorrt10_ms']:.2f}倍，CPU ONNX为{s['cpu_onnx_ms'] / n['cpu_onnx_ms']:.2f}倍。只能在各自同一列内做描述性比较，不把CPU与GPU直接比较。
- 两者体现精度与资源成本的取舍，没有一个在所有指标上占优。选型取决于设备和任务要求，不自动宣布S更适合所有场景。

## 评估口径与来源检查

1. 发布表：目标检测、COCO验证集、输入640。普通检测使用one-to-many与NMS；端到端使用one-to-one、无需NMS。速度选择后者，因此精度/速度联合分析采用端到端列。
2. 参数量与FLOPs属于融合后的部署模型，且去掉未使用分支；不能和完整训练checkpoint的参数直接等同。
3. T4与TensorRT10是官方声明的运行条件。模型页未完整列出CPU型号、计时batch、数值精度和耗时范围；这些保留为未知，不能声称独立核验了所有测速条件，也不能推断本机实时帧率。
4. 训练参数允许不同：官方说明COCO超参数经过进化搜索。这里比较整体发布方案，不做“仅模型大小变化”的因果实验，也不宣称搜索得到绝对最优。
5. 当前网页是{source['accessed_date']}读取的动态文档，不是v8.4.0发布资产的冻结性能证明。表中数值是有来源的人工转录，未运行网页自动抓取，也未独立复现实验。

## 与旧发布文件中保存的成绩分开

| 来源 | N | S | 尺度与模式 |
|---|---:|---:|---|
| v8.4.0 checkpoint保存mAP | {n['checkpoint_saved_map50_95_pct']:.3f} | {s['checkpoint_saved_map50_95_pct']:.3f} | 原0–1值乘100；head未独立核实 |
| 当前网页普通检测mAP | {n['map50_95_standard_pct']} | {s['map50_95_standard_pct']} | 0–100，one-to-many |
| 当前网页端到端mAP | {n['map50_95_e2e_pct']} | {s['map50_95_e2e_pct']} | 0–100，one-to-one |

保存值数值上接近网页端到端列，但相近不能证明模式和评估版本一致。总表保留独立字段，不用网页成绩覆盖保存指标，也不把保存指标标成已确认的端到端成绩。

## 文件与使用

- [性能CSV总表](performance_summary.csv)：一行一个模型，单位写在列名中；未知值为空，不当作0。
- [输入来源记录](../../../data/reference/yolo26-official-benchmark-2026-10-24.json)：网页表格转录及口径说明。
- 程序：`python experiment-analysis/tools/build_performance_summary.py`。输出目录存在时拒绝覆盖。

来源：[官方模型性能表]({source['source_url']})；[官方训练配方]({source['recipe_url']})。
"""


def run(source_path=SOURCE, official=OFFICIAL, output=OUTPUT):
    if output.exists():
        raise FileExistsError("Output exists; choose a new directory")
    source = read_json(source_path)
    rows = build_rows(source, official)
    text = report(rows, source)
    output.mkdir(parents=True)
    with (output / "performance_summary.csv").open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output / "README.md").write_text(text, encoding="utf-8")
    return {"models": len(rows), "output": str(output)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--official", type=Path, default=OFFICIAL)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.source, args.official, args.output), ensure_ascii=False))
    except (OSError, ValueError, KeyError) as exc:
        parser.exit(1, f"Performance summary failed: {exc}\n")


if __name__ == "__main__":
    main()
