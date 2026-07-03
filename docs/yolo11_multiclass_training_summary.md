# YOLO11 Multiclass Training Summary

This document summarizes the first formal YOLO11 multiclass experiment for the DirtNet reproduction project. This experiment is separate from the binary dirt-versus-object experiments already present in this repository.

## Task Definition

- Task: 10-class object detection
- Model: YOLO11m with COCO pretraining
- Dataset type: synthetic training and validation images
- Training date: June 30, 2026
- Main metric: mAP50-95

The model predicts the following classes:

| ID | Class |
|---:|---|
| 0 | `dirt` |
| 1 | `business_cards` |
| 2 | `keys` |
| 3 | `other` |
| 4 | `paper_and_notebooks` |
| 5 | `pens` |
| 6 | `rulers` |
| 7 | `scissors` |
| 8 | `tapes` |
| 9 | `usb_sticks` |

## Dataset

| Split | Images | Instances | Purpose |
|---|---:|---:|---|
| Train | 860 | 8,626 | Parameter learning |
| Validation | 296 | 2,962 | Per-epoch evaluation and best-checkpoint selection |
| `test_real_new` | 80 | 644 | Held-out real-image test; not used in this experiment |

The training labels are imbalanced. The `dirt` class contains 5,161 instances, while `scissors` contains 114 instances and both `rulers` and `tapes` contain 162 instances.

Dataset configuration: [`multiclass_small.yaml`](../multiclass_small.yaml)

## Training Setup

| Setting | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 3060 Laptop GPU, 6 GB |
| Python | 3.12.10 |
| PyTorch | 2.12.1+cu130 |
| Ultralytics | 8.4.74 |
| Model | YOLO11m |
| Fused parameters | 20,037,742 |
| Input size | 1024 |
| Batch size | 2 |
| Epochs | 30 |
| Optimizer | `auto` |
| AMP | enabled |
| Workers | 0 |
| Seed | 0 |
| Deterministic mode | enabled |

The complete effective configuration is stored in [`args.yaml`](../runs/detect/yolo11m_multiclass_e30_i1024_b2/args.yaml).

## Validation Results

Training completed all 30 epochs in 5,045.91 seconds, or approximately 84.1 minutes. No CUDA out-of-memory error occurred. The best checkpoint was selected at epoch 29.

| Metric | Best, epoch 29 | Last, epoch 30 |
|---|---:|---:|
| Precision | 0.9535 | 0.9415 |
| Recall | 0.9305 | 0.9387 |
| mAP50 | 0.9608 | 0.9581 |
| mAP50-95 | 0.8136 | 0.8082 |
| Training box loss | 0.6516 | 0.6363 |
| Validation box loss | 0.7059 | 0.7349 |

The training loss continued to decrease in the final epoch, but the validation box loss increased and both mAP metrics declined slightly. The epoch-29 checkpoint is therefore the selected model.

## Per-Class Validation AP50

| Class | AP50 |
|---|---:|
| `business_cards` | 0.995 |
| `paper_and_notebooks` | 0.995 |
| `scissors` | 0.995 |
| `tapes` | 0.995 |
| `pens` | 0.994 |
| `keys` | 0.982 |
| `other` | 0.961 |
| `usb_sticks` | 0.924 |
| `dirt` | 0.908 |
| `rulers` | 0.860 |

`rulers` is the weakest validation class. Its limited sample count and thin geometry make localization difficult. The appearance and scale variation of `dirt` also makes its boundary definition harder than the office-item classes.

## Convergence Assessment

The [training curves](../runs/detect/yolo11m_multiclass_e30_i1024_b2/results.png) show that:

- all three training losses decreased throughout training;
- validation losses decreased overall with only minor late-stage variation;
- mAP50 and mAP50-95 improved until epoch 29; and
- there was no sustained validation degradation indicating severe overfitting.

Thirty epochs is therefore a suitable baseline. Additional synthetic-only epochs may produce a small improvement, but they are unlikely to solve the real-image generalization gap.

## Result Artifacts

- [Per-epoch metrics](../runs/detect/yolo11m_multiclass_e30_i1024_b2/results.csv)
- [Training curves](../runs/detect/yolo11m_multiclass_e30_i1024_b2/results.png)
- [Precision-recall curves](../runs/detect/yolo11m_multiclass_e30_i1024_b2/BoxPR_curve.png)
- [Normalized confusion matrix](../runs/detect/yolo11m_multiclass_e30_i1024_b2/confusion_matrix_normalized.png)

Model weights are intentionally excluded from Git. The selected checkpoint SHA-256 is `EFC9968722A442C3A6D95D4B6186D62C0A3FE3FDC322439DA2D02D409D153790`.

## Conclusion

YOLO11m successfully completed 10-class training at `imgsz=1024` and `batch=2` on a 6 GB GPU. The strong synthetic validation result confirms that the label conversion, multiclass detection head, and training pipeline are functional. Performance on synthetic validation data must not be interpreted as real-robot performance; the held-out real-image evaluation is documented separately.
