# Step 1 mapping verification

Read-only input checks passed on 2026-10-26. This is not database/import/query validation.

- YOLO26n: published numeric values, saved mAP raw/conversion, source hash/date/URL, missing timing fields, selected config values agree; 113 config keys and 11 saved metrics present.
- YOLO26s: published numeric values, saved mAP raw/conversion, source hash/date/URL, missing timing fields, selected config values agree; 113 config keys and 11 saved metrics present.
- Field inventory contains 385 leaf/CSV-column entries across 10 files. observed_missing describes current data only, not a future constraint.
- Expected selection evaluated directly from source JSON: only YOLO26s satisfies e2e mAP >=45 and T4 latency <=3. No SQL executed.

| Model | Source | Purpose | Original field | Value |
|---|---|---|---|---:|
| YOLO26n | published transcription | accuracy | map50_95_standard_pct | 40.9 |
| YOLO26n | published transcription | accuracy | map50_95_e2e_pct | 40.1 |
| YOLO26n | published transcription | latency | cpu_onnx_ms | 38.9 |
| YOLO26n | published transcription | latency | t4_tensorrt10_ms | 1.7 |
| YOLO26n | published transcription | complexity | params_m | 2.4 |
| YOLO26n | published transcription | complexity | flops_b | 5.5 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/precision(B) | 0.64948 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/recall(B) | 0.50734 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/mAP50(B) | 0.55715 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/mAP50-95(B) | 0.40116 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/mAP_small(B) | 0.1968 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/mAP_medium(B) | 0.44133 |
| YOLO26n | checkpoint N | accuracy / head unverified | metrics/mAP_large(B) | 0.58232 |
| YOLO26n | checkpoint N | accuracy / head unverified | val/box_loss | 0.99458 |
| YOLO26n | checkpoint N | accuracy / head unverified | val/cls_loss | 1.63686 |
| YOLO26n | checkpoint N | accuracy / head unverified | val/dfl_loss | 0.06102 |
| YOLO26n | checkpoint N | accuracy / head unverified | fitness | 0.41676 |
| YOLO26s | published transcription | accuracy | map50_95_standard_pct | 48.6 |
| YOLO26s | published transcription | accuracy | map50_95_e2e_pct | 47.8 |
| YOLO26s | published transcription | latency | cpu_onnx_ms | 87.2 |
| YOLO26s | published transcription | latency | t4_tensorrt10_ms | 2.5 |
| YOLO26s | published transcription | complexity | params_m | 9.5 |
| YOLO26s | published transcription | complexity | flops_b | 20.9 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/precision(B) | 0.69674 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/recall(B) | 0.5811 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/mAP50(B) | 0.64598 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/mAP50-95(B) | 0.47769 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/mAP_small(B) | 0.28974 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/mAP_medium(B) | 0.52532 |
| YOLO26s | checkpoint S | accuracy / head unverified | metrics/mAP_large(B) | 0.64496 |
| YOLO26s | checkpoint S | accuracy / head unverified | val/box_loss | 1.50982 |
| YOLO26s | checkpoint S | accuracy / head unverified | val/cls_loss | 1.55169 |
| YOLO26s | checkpoint S | accuracy / head unverified | val/dfl_loss | 0.00545 |
| YOLO26s | checkpoint S | accuracy / head unverified | fitness | 0.49452 |

## Input manifest

```json
[
  {
    "path": "data/reference/yolo26-official-benchmark-2026-10-24.json",
    "bytes": 1602,
    "sha256": "7f8ea25314849a03e3f2b1588d8ca2f106d52c45e8618e5e4672387dd47624a7"
  },
  {
    "path": "reports/official/performance-n-s-2026-10-24/performance_summary.csv",
    "bytes": 1197,
    "sha256": "2bea1dac6cd8e397fe3bef50b673b1e33aef015e130062d98a4b3bcc56745e0b"
  },
  {
    "path": "reports/official/yolo26n-v8.4.0/source.json",
    "bytes": 1418,
    "sha256": "37637266a91a157b241b0bd349062546f0c565186f78778e19dd362bd0e3e269"
  },
  {
    "path": "reports/official/yolo26n-v8.4.0/training_config.json",
    "bytes": 2472,
    "sha256": "f137bbb3273639c0c4baa96353e3294c5a96f3025bc665a14397b83dd5577a68"
  },
  {
    "path": "reports/official/yolo26n-v8.4.0/saved_metrics.json",
    "bytes": 356,
    "sha256": "de171a22c16f885d8efb82e54bb2c978bc994d4a10762aeab8371732e86945f7"
  },
  {
    "path": "reports/official/yolo26n-v8.4.0/checkpoint_metadata.json",
    "bytes": 358,
    "sha256": "9ff6938c3a001b028061c78bf1299792a0921a10a2a81a147e1d7e4ede654778"
  },
  {
    "path": "reports/official/yolo26s-v8.4.0/source.json",
    "bytes": 1413,
    "sha256": "4ed696fa0f07d570d805acba85c7b4f9a05b16c5ae2b8802502ccc92d7d3cae5"
  },
  {
    "path": "reports/official/yolo26s-v8.4.0/training_config.json",
    "bytes": 2490,
    "sha256": "63318bc0b05e03da8a07a101108d3ef10d1a54405342a17b916d4633c7ddd3a6"
  },
  {
    "path": "reports/official/yolo26s-v8.4.0/saved_metrics.json",
    "bytes": 356,
    "sha256": "fa52ee91f90679897f73bb3251890e648a647be81b9a0d35685e0a62b0cf1a52"
  },
  {
    "path": "reports/official/yolo26s-v8.4.0/checkpoint_metadata.json",
    "bytes": 352,
    "sha256": "ac0b1ec926ad9c724802b0238a32322a780f4736b5bda69dc4c56dea1797a33e"
  }
]
```
