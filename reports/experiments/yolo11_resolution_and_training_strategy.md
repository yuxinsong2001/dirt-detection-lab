# YOLO11 Resolution and Training Strategy Update

This document summarizes the optimization steps after the earlier YOLO11s baseline was selected. At that point, the main setting was:

- Model: YOLO11s
- Dataset: `binary_full.yaml`
- Optimizer: SGD
- AMP: enabled
- Augmentation: default detection augmentation
- Main metric: mAP50

The goal of this stage was to check whether the model should be improved by longer training, higher input resolution, rectangular training, learning-rate scheduling, or mosaic changes.

## 1. Longer Training at 1024

The first follow-up experiment extended YOLO11s training from 15 epochs to 30 epochs at `imgsz=1024`.

| Experiment | imgsz | Epochs | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_e15_b8` | 1024 | 15 | 0.963 | 0.923 | 0.959 | 0.844 | 2096.9s |
| `yolo11s_full_sgd_e30_b8` | 1024 | 30 | 0.961 | 0.934 | 0.962 | 0.872 | 4039.7s |

The 30-epoch run improved recall and mAP50-95 clearly, while mAP50 only increased slightly. This means longer training improves localization quality, but the time cost almost doubles.

Conclusion:

- 30 epochs is useful and should be applied in final training.
- During parameter optimization, 15 epochs is kept as the faster screening setting.
- The improvement suggested that the model was still learning, but training length alone was not the strongest lever.

## 2. Higher Input Resolution

The next major experiment changed `imgsz` from 1024 to 1280 while keeping the YOLO11s + SGD setting.

| Experiment | imgsz | Epochs | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_e15_b8` | 1024 | 15 | 0.963 | 0.923 | 0.959 | 0.844 | 2096.9s |
| `yolo11s_full_sgd_e30_b8` | 1024 | 30 | 0.961 | 0.934 | 0.962 | 0.872 | 4039.7s |
| `yolo11s_full_sgd_img1280_e15_b8` | 1280 | 15 | 0.976 | 0.944 | 0.977 | 0.876 | 3208.3s |

The 1280-resolution run outperformed both 1024 runs, including the 30-epoch 1024 run. This is the most important result in this stage.

Compared with `1024 e15`, `1280 e15` improved:

- mAP50 by 0.018
- recall by 0.021
- mAP50-95 by 0.032

Compared with `1024 e30`, `1280 e15` still improved:

- mAP50 by 0.015
- recall by 0.010
- mAP50-95 by 0.004

Conclusion:

- Input resolution is more important than simply increasing epochs for this task.
- The task appears to benefit from preserving image details.
- YOLO11s at 1280 becomes the new main candidate.

## 3. Comparison with YOLO11m at 1024

The 1280-resolution YOLO11s result was also compared with the previous YOLO11m result at 1024.

| Experiment | Model | imgsz | Epochs | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `yolo11m_full_sgd_e15_b8` | YOLO11m | 1024 | 15 | 0.965 | 0.939 | 0.971 | 0.875 | 4114.2s |
| `yolo11s_full_sgd_img1280_e15_b8` | YOLO11s | 1280 | 15 | 0.976 | 0.944 | 0.977 | 0.876 | 3208.3s |

YOLO11s at 1280 outperformed YOLO11m at 1024 while also taking less training time.

Conclusion:

- For this dataset, increasing input resolution is more effective than increasing model size.
- YOLO11m at 1280 should theoretically provide stronger performance, because it combines a larger model with the higher-resolution input.
- However, this setting is much more expensive and machine limits, especially GPU memory, become the main bottleneck.
- YOLO11m at 1280 is therefore treated as a high-cost upper-bound candidate, not as the main optimization route.
- The current practical model choice is YOLO11s at 1280.

## 4. Rectangular Training

Because the source images are not square, `rect=True` was tested at 1280 resolution. It is important to note that in the current YOLO training pipeline, `rect=True` disables mosaic augmentation because rectangular training and mosaic are incompatible.

| Experiment | rect | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_img1280_e15_b8` | false | 0.976 | 0.944 | 0.977 | 0.876 | 3208.3s |
| `yolo11s_full_sgd_img1280_rect_e15_b8` | true | 0.969 | 0.941 | 0.975 | 0.868 | 2553.6s |

`rect=True` reduced training time by about 20.4%, but the accuracy was slightly lower. The mAP50 drop was small, but mAP50-95 dropped more clearly.

Conclusion:

- `rect=True` is useful as an efficient training option.
- It is not the best setting for maximum accuracy.
- The accuracy drop is likely related to the fact that rectangular training is incompatible with mosaic augmentation.

## 5. Mosaic Ablation

To understand the `rect=True` result, mosaic was disabled separately while keeping `rect=False`.

| Experiment | mosaic | rect | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_img1280_e15_b8` | 1.0 | false | 0.976 | 0.944 | 0.977 | 0.876 | 3208.3s |
| `yolo11s_full_sgd_img1280_nomosaic_e15_b8` | 0.0 | false | 0.971 | 0.944 | 0.975 | 0.871 | 3198.8s |
| `yolo11s_full_sgd_img1280_rect_e15_b8` | disabled by rect | true | 0.969 | 0.941 | 0.975 | 0.868 | 2553.6s |

The no-mosaic result is close to the rect result in mAP50. This supports the interpretation that the small accuracy drop from `rect=True` is mainly caused by losing mosaic augmentation, not by rectangular batching itself.

Conclusion:

- Mosaic should be kept for the accuracy-focused configuration.
- Disabling mosaic does not provide a meaningful speed gain unless `rect=True` is also used.
- The default mosaic setting remains the better choice for final accuracy.

## 6. Cosine Learning Rate

The cosine learning-rate scheduler was tested at 1280 resolution.

| Experiment | cos_lr | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_img1280_e15_b8` | false | 0.976 | 0.944 | 0.977 | 0.876 | 3208.3s |
| `yolo11s_full_sgd_img1280_cos_e15_b8` | true | 0.965 | 0.941 | 0.974 | 0.876 | 3199.9s |

`cos_lr=True` did not improve the result. mAP50 and recall were lower than the baseline, while mAP50-95 was almost unchanged.

Conclusion:

- Do not use `cos_lr=True` for the current main configuration.
- Keep the default linear learning-rate schedule.

## 7. Current Decision

The current accuracy-focused candidate is:

```text
YOLO11s + imgsz=1280 + batch=8 + epochs=15 + optimizer=SGD + default detection augmentation
```

This corresponds to:

```text
yolo11s_full_sgd_img1280_e15_b8
```

The current efficient candidate is:

```text
YOLO11s + imgsz=1280 + batch=8 + epochs=15 + optimizer=SGD + rect=True
```

This corresponds to:

```text
yolo11s_full_sgd_img1280_rect_e15_b8
```

## 8. Next Step

No more broad parameter search is needed at this point.

The next stage should run a small number of final, more expensive training comparisons. These should apply the selected settings for longer training and compare only the most meaningful final candidates.

The main purpose is no longer broad parameter search, but final model selection under realistic training cost.
