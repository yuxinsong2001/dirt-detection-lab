# Official YOLO26n / YOLO26s configuration comparison

Descriptive comparison of saved values only. No model ranking or causal conclusion.

Training fields: 113; counts: {"same": 77, "different": 36}.
Saved curve rows: N=245, S=70.

## Selected recorded settings

| Field | YOLO26n | YOLO26s |
|---|---|---|
| task | "detect" | "detect" |
| data | "/home/lq/codes/ultralytics/ultralytics/cfg/datasets/coco.yaml" | "/home/lq/codes/ultralytics/ultralytics/cfg/datasets/coco.yaml" |
| model | "yolo26n-objv1-150.pt" | "yolo26s-objv1-150.pt" |
| epochs | 245 | 70 |
| imgsz | 640 | 640 |
| batch | 128 | 128 |
| optimizer | "MuSGD" | "MuSGD" |
| seed | 0 | 0 |
| lr0 | 0.0054 | 0.00038 |
| lrf | 0.04952 | 0.88219 |
| mosaic | 0.90863 | 0.99182 |
| mixup | 0.01216 | 0.05 |
| scale | 0.56232 | 0.9 |
| device | "5" | "3" |

## Interpretation limits

- Matching data paths record the same YAML location, not proof of identical image/annotation bytes.
- Training budgets, starting checkpoints, learning rates and augmentations differ. This is not a one-variable controlled comparison.
- Both report the same library version, but the producing Git commits differ. Do not assume identical training/evaluation code.
- Device values such as 3 and 5 are device indices, not GPU model names. They do not establish comparable hardware or speed.
- These are saved training settings. Null or automatic values do not prove a resolved evaluation setting; for example, conf=null is not a known confidence threshold.
- Keep saved checkpoint metrics separate from the final curve row. Do not choose a best epoch by guessing.
- Loss-column names alone do not guarantee the same loss formula across code revisions.
- No accuracy or latency ranking is generated. Later comparisons need an explicit protocol and evidence for missing conditions.

## Inputs

- [N configuration](../yolo26n-v8.4.0/training_config.json)
- [S configuration](../yolo26s-v8.4.0/training_config.json)
- [All fields and statuses](config_comparison.csv)

CSV status values are same, different, missing_n or missing_s. Values retain JSON types; null is distinct from a missing field.
