# YOLO11 Final Experiment Summary

This document summarizes the final YOLO11 binary detection experiments after the earlier parameter search. The selected training direction before this stage was:

- Dataset config: `binary_full.yaml`
- Task: 2-class detection
- Optimizer: SGD
- Input size: `imgsz=1280`
- Augmentation: default detection augmentation
- AMP: enabled
- Final training length: 30 epochs
- Main model sizes: YOLO11s and YOLO11m

The purpose of this stage was to train the final candidates and then evaluate their ability on the independent `test_real_new` split.

## 1. Pre-Training Feasibility Tests

Before running the final 30-epoch training, three short YOLO11m tests were used to check whether the expensive `imgsz=1280` setting was feasible on the available machine.

| Experiment | Model | imgsz | Batch | Rect | Epochs | Result |
|---|---|---:|---:|---:|---:|---|
| `yolo11m_test_img1280_sgd_e1_b8` | YOLO11m | 1280 | 8 | false | 1 | manually stopped |
| `yolo11m_test_img1280_sgd_rect_e1_b8` | YOLO11m | 1280 | 8 | true | 1 | manually stopped |
| `yolo11m_test_img1280_sgd_e1_b4` | YOLO11m | 1280 | 4 | false | 1 | completed |

The first `batch=8` test showed very high GPU memory pressure. Training became abnormally slow, so it was manually stopped instead of being used for the final long run.

After that, `rect=True` was tested because rectangular training can reduce unnecessary padding and may lower memory or computation cost for non-square images. However, the `batch=8 + rect=True` run was still too slow under the current hardware limit, so it was also manually stopped.

The `batch=4` test completed successfully:

| Experiment | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|
| `yolo11m_test_img1280_sgd_e1_b4` | 89.5% | 85.9% | 90.7% | 71.3% | 452.6s |

This one-epoch result was not used to judge final model quality. Its purpose was to confirm that YOLO11m could complete training at `imgsz=1280` when `batch=4` was used.

The `rect=True` test was not continued as the final setting. Earlier experiments had already shown that rectangular training disables mosaic and slightly reduces accuracy. Since `rect=True` did not make `batch=8` practical enough, the final YOLO11m run used the normal accuracy-focused setting with `batch=4`.

## 2. Final Training Setup

Two final candidates were trained:

| Experiment | Model | imgsz | Batch | Epochs | Optimizer |
|---|---|---:|---:|---:|---|
| `yolo11s_final_img1280_sgd_e30_b8` | YOLO11s | 1280 | 8 | 30 | SGD |
| `yolo11m_final_img1280_sgd_e30_b4` | YOLO11m | 1280 | 4 | 30 | SGD |

YOLO11m could not be trained comfortably with `batch=8` at `imgsz=1280`, so `batch=4` was used for the final YOLO11m run. Rectangular training was not used for the final accuracy-focused setting because earlier experiments showed that `rect=True` disables mosaic and slightly reduces accuracy.

## 3. Validation Results

The final validation results were:

| Experiment | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|
| `yolo11s_final_img1280_sgd_e30_b8` | 97.2% | 95.1% | 97.9% | 90.6% |
| `yolo11m_final_img1280_sgd_e30_b4` | 97.4% | 96.2% | 98.3% | 92.3% |

On the validation set, YOLO11m is the best model. It improves recall, mAP50, and mAP50-95 compared with YOLO11s. The largest difference is in mAP50-95, which suggests that YOLO11m produces better localization quality on the validation distribution.

Based only on validation-set model selection, YOLO11m is therefore the validation-selected model.

## 4. Independent Test Results

Both final models were then evaluated on the independent `test_real_new` split.

| Experiment | Precision | Recall | mAP50 | mAP50-95 | Inference |
|---|---:|---:|---:|---:|---:|
| `yolo11s_final_img1280_sgd_e30_b8_test_real_new` | 78.1% | 77.2% | 80.6% | 56.2% | 10.0 ms/img |
| `yolo11m_final_img1280_sgd_e30_b4_test_real_new` | 83.5% | 70.4% | 77.8% | 53.2% | 21.4 ms/img |

The independent test result differs from the validation result. YOLO11m has higher precision, but YOLO11s has higher recall, higher mAP50, higher mAP50-95, and faster inference.

This indicates that YOLO11m is more conservative on real unseen images. It produces fewer false positives, but it misses more targets. YOLO11s gives a better balance on `test_real_new`, especially because recall and mAP50 are important for the dirt detection task.

## 5. Class-Level Test Results

The class-level results on `test_real_new` were:

| Model | Class | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|
| YOLO11s | dirt | 84.7% | 69.3% | 76.2% | 45.9% |
| YOLO11s | object | 71.6% | 85.2% | 85.1% | 66.6% |
| YOLO11m | dirt | 87.7% | 66.9% | 75.4% | 44.7% |
| YOLO11m | object | 79.3% | 73.9% | 80.2% | 61.6% |

For the `dirt` class, YOLO11m has slightly higher precision, but YOLO11s has better recall and mAP50. For the `object` class, YOLO11s is also stronger in recall and mAP50.

The lower test performance compared with validation suggests a clear distribution shift between the validation split and the real test split.

## 6. Final Interpretation

The final result contains two model roles:

1. **Validation-selected model:** `yolo11m_final_img1280_sgd_e30_b4`
2. **Practical recommended model:** `yolo11s_final_img1280_sgd_e30_b8`

This distinction is important. The model was not re-optimized using `test_real_new`. Instead, the validation set selected YOLO11m, while the independent real test set revealed that YOLO11s generalizes better under domain shift.

The final conclusion is:

- YOLO11m is the strongest model on the validation distribution.
- YOLO11s is more suitable as the practical final recommendation because it performs better on real unseen images and is faster.
- The gap between validation and `test_real_new` should be discussed as a domain-shift issue.
- Future improvement should focus on increasing real-image diversity in training and validation, rather than only increasing model size.
