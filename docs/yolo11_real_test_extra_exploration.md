# YOLO11 Real-Test Extra Exploration

This document records the additional exploration after the final YOLO11 training stage. The motivation was that the validation-selected YOLO11m model did not perform best on the independent `test_real_new` split.

The first real-test comparison showed that the final YOLO11s model performed better than the final YOLO11m model. After that, the earlier 1024-resolution YOLO11s model was also tested and performed even better. This led to a broader real-test sweep over the available YOLO11s and YOLO11m runs.

The goal of this extra exploration was not to repeatedly tune on the test set. Instead, the test results were used to understand why the validation-selected direction did not transfer well to real images.

## 1. Why This Exploration Was Needed

Before this stage, the main validation-selected setting was:

```text
YOLO11m + imgsz=1280 + SGD + 30 epochs
```

On the validation set, this model achieved the strongest result:

| Model | imgsz | Epochs | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| `yolo11s_final_img1280_sgd_e30_b8` | 1280 | 30 | 97.2% | 95.1% | 97.9% | 90.6% |
| `yolo11m_final_img1280_sgd_e30_b4` | 1280 | 30 | 97.4% | 96.2% | 98.3% | 92.3% |

However, on `test_real_new`, the same final models performed much worse:

| Model | imgsz | Epochs | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| `yolo11s_final_img1280_sgd_e30_b8` | 1280 | 30 | 78.1% | 77.2% | 80.6% | 56.2% |
| `yolo11m_final_img1280_sgd_e30_b4` | 1280 | 30 | 83.5% | 70.4% | 77.8% | 53.2% |

This contradiction suggested that the validation set was not a reliable proxy for real-image performance. It also made it necessary to check whether the earlier, simpler YOLO11s models were actually stronger on real images.

## 2. YOLO11s and YOLO11m Real-Test Sweep

All available YOLO11s and YOLO11m models were evaluated on `test_real_new`. The combined sweep results are:

| Model | Experiment | imgsz | Precision | Recall | mAP50 | mAP50-95 | Inference |
|---|---|---:|---:|---:|---:|---:|---:|
| YOLO11s | `yolo11s_full_sgd_e15_b8` | 1024 | 83.7% | 84.5% | 88.5% | 62.3% | 6.2 ms |
| YOLO11s | `yolo11s_full_sgd_aligned_aug_e15_b8` | 1024 | 83.7% | 84.5% | 88.5% | 62.3% | 6.2 ms |
| YOLO11m | `yolo11m_test_img1280_sgd_e1_b4` | 1280 | 79.9% | 82.3% | 88.1% | 63.1% | 21.3 ms |
| YOLO11m | `yolo11m_full_sgd_e15_b8` | 1024 | 84.1% | 83.5% | 87.8% | 62.3% | 14.3 ms |
| YOLO11s | `yolo11s_full_sgd_aligned_aug_amp_false_e15_b8` | 1024 | 82.9% | 83.4% | 87.5% | 62.5% | 6.3 ms |
| YOLO11s | `yolo11s_full_default_e15_b8` | 1024 | 81.8% | 80.5% | 85.3% | 60.2% | 6.2 ms |
| YOLO11s | `yolo11s_full_sgd_e30_b8` | 1024 | 83.7% | 77.4% | 84.5% | 58.9% | 6.4 ms |
| YOLO11s | `yolo11s_full_sgd_img1280_nomosaic_e15_b8` | 1280 | 79.2% | 78.4% | 82.8% | 58.7% | 9.5 ms |
| YOLO11s | `yolo11s_full_sgd_img1280_rect_e15_b8` | 1280 | 79.0% | 77.6% | 82.4% | 57.7% | 9.7 ms |
| YOLO11s | `yolo11s_full_sgd_img1280_cos_e15_b8` | 1280 | 78.3% | 79.6% | 82.2% | 59.1% | 9.7 ms |
| YOLO11s | `yolo11s_full_sgd_img1280_e15_b8` | 1280 | 86.5% | 72.3% | 82.0% | 57.6% | 9.7 ms |
| YOLO11s | `yolo11s_final_img1280_sgd_e30_b8` | 1280 | 78.1% | 77.2% | 80.6% | 56.2% | 9.6 ms |
| YOLO11m | `yolo11m_final_img1280_sgd_e30_b4` | 1280 | 83.5% | 70.4% | 77.8% | 53.2% | 21.4 ms |
| YOLO11m | `yolo11m_full_default_e15_b8` | 1024 | 80.8% | 71.1% | 77.8% | 54.3% | 14.2 ms |

The strongest result on `test_real_new` was the simple YOLO11s 1024-resolution SGD run with 15 epochs. The 1280-resolution settings were consistently worse on the real test split, even though 1280 had been better on the validation set.

The surprising result was that the one-epoch feasibility run, `yolo11m_test_img1280_sgd_e1_b4`, performed better on `test_real_new` than the final 30-epoch YOLO11m model. The result suggests that a small amount of adaptation may preserve general pretrained features better than long training on the synthetic-domain data.

## 3. Short-Training Check

To check whether the strong one-epoch result was accidental, a simple short-training experiment was added for both YOLO11s and YOLO11m:

```text
imgsz=1024, batch=8, epochs=1, optimizer=SGD
```

| Experiment | imgsz | Precision | Recall | mAP50 | mAP50-95 | Inference |
|---|---:|---:|---:|---:|---:|---:|
| `yolo11s_short_sgd_e1_b8` | 1024 | 82.5% | 81.5% | 87.5% | 63.4% | 6.2 ms |
| `yolo11m_short_sgd_e1_b8` | 1024 | 80.0% | 81.3% | 87.1% | 63.9% | 14.3 ms |

These short-training results are close to the best 15-epoch real-test results. This supports the idea that YOLO adapts quickly to the two-class task and that longer training can reduce real-domain generalization when the training/validation distribution differs from the real test distribution.

## 4. Interpretation

The main issue appears to be domain shift, not model capacity.

The training and validation data contain synthetic or blended data, while `test_real_new` contains real images. Their visual statistics can differ in texture, illumination, dirt shape, object appearance, boundary clarity, and label style. As a result, a model that becomes better on the validation distribution may become less suitable for the real-image distribution.

The most likely explanation is:

1. The synthetic training and validation data do not fully represent real images.
2. YOLO learns the two-class task quickly from pretrained weights.
3. Longer training makes the model fit the synthetic/validation distribution more strongly.
4. Higher resolution may amplify texture-level differences between synthetic and real images.
5. Larger models may fit domain-specific patterns more strongly than smaller models.

The pretrained weights do not know the project-specific `dirt` and `object` labels. However, they provide general detection features such as edges, shapes, textures, objectness, and localization priors. A short fine-tuning stage may be enough to map these generic features to the two new classes, while long fine-tuning can over-specialize the model to the synthetic domain.

Additional factors may also contribute to the result:

- The `object` class is broad, and its appearance may differ strongly between synthetic/blended data and real images.
- Labeling standards may not be fully consistent, especially for dirt boundaries, small stains, blurred regions, or ambiguous objects.
- `imgsz=1280` may amplify domain differences because the model can rely more on fine texture details that differ between synthetic and real images.
- Short training may preserve more general pretrained features, while long training may shift the model toward synthetic-domain dirt patterns.

## 5. How Test Results Should Be Used

In a strict experimental setup, the final test set should not be used repeatedly to choose hyperparameters. Repeatedly selecting models based on `test_real_new` would make it no longer a clean final test set.

However, the current situation is different from normal hyperparameter tuning. The test results revealed that the validation set and real test set lead to nearly opposite conclusions. Therefore, `test_real_new` is useful as a diagnostic signal:

- It shows that the current validation split is not a strong proxy for real images.
- It suggests that the main limitation is the data distribution, not the YOLO architecture.
- It justifies reporting real-test behavior separately from validation behavior.
- It motivates a practical recommendation without pretending that validation performance fully reflects deployment behavior.

For this project stage, it is not realistic to build a new real-image validation set or run many more complex experiments. The most reasonable response is to clearly report the domain-shift finding and avoid over-claiming that the validation-best model is the best real-world model.

## 6. Current Practical Conclusion

The validation-selected model remains:

```text
yolo11m_final_img1280_sgd_e30_b4
```

It is the strongest model on the validation distribution.

The practical real-test recommendation is:

```text
yolo11s_full_sgd_e15_b8
```

This model has the best overall `test_real_new` mAP50, high recall, and the fastest inference among the best-performing candidates.

The short-training experiments also suggest that early checkpoints are worth considering:

```text
yolo11s_short_sgd_e1_b8
yolo11m_short_sgd_e1_b8
```

They are not chosen as final models, but they support the conclusion that short fine-tuning can generalize well when the target real domain differs from the synthetic training domain.
