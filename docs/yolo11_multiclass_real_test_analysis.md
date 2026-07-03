# YOLO11 Multiclass Real-Test Analysis

This document evaluates the synthetic-data-trained YOLO11m multiclass model on the independent `test_real_new` split. The task contains 10 classes and is distinct from the repository's binary dirt-versus-object evaluations.

## Evaluation Setup

| Setting | Value |
|---|---|
| Task | 10-class object detection |
| Model | Best checkpoint from the multiclass training experiment |
| Checkpoint epoch | 29 |
| Test split | `test_real_new` |
| Images | 80 |
| Instances | 644 |
| Background-only images | 0 |
| Input size | 1024 |
| Batch size | 1 |
| Device | CUDA:0 |

The test images did not participate in training, validation, or checkpoint selection.

## Overall Results

| Precision | Recall | mAP50 | mAP50-95 |
|---:|---:|---:|---:|
| 0.665 | 0.776 | 0.737 | 0.554 |

The best overall F1 score is approximately 0.70 at a confidence threshold near 0.294. A deployment threshold between 0.25 and 0.30 is a reasonable starting point, but the final threshold must reflect the relative cost of missed dirt and false cleaning alarms.

## Per-Class Results

| Class | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| `dirt` | 80 | 360 | 0.852 | 0.706 | 0.773 | 0.489 |
| `business_cards` | 34 | 41 | 0.892 | 0.756 | 0.852 | 0.685 |
| `keys` | 23 | 23 | 0.466 | 0.783 | 0.639 | 0.461 |
| `other` | 19 | 19 | 0.276 | 0.632 | 0.404 | 0.283 |
| `paper_and_notebooks` | 49 | 61 | 0.802 | 0.869 | 0.878 | 0.695 |
| `pens` | 34 | 39 | 0.934 | 0.974 | 0.986 | 0.797 |
| `rulers` | 23 | 23 | 0.539 | 0.508 | 0.490 | 0.353 |
| `scissors` | 26 | 26 | 0.677 | 0.923 | 0.922 | 0.816 |
| `tapes` | 24 | 24 | 0.723 | 1.000 | 0.903 | 0.599 |
| `usb_sticks` | 28 | 28 | 0.485 | 0.607 | 0.520 | 0.360 |

The strongest classes are `pens`, `scissors`, `paper_and_notebooks`, and `business_cards`. The weakest classes are `other`, `rulers`, and `usb_sticks`. The high recall but low precision for `keys` indicates that most keys are found, but unrelated objects and reflections also trigger key predictions.

## Synthetic-to-Real Generalization Gap

| Metric | Synthetic validation | Real test | Absolute decrease |
|---|---:|---:|---:|
| Precision | 0.953 | 0.665 | 0.288 |
| Recall | 0.930 | 0.776 | 0.154 |
| mAP50 | 0.961 | 0.737 | 0.224 |
| mAP50-95 | 0.814 | 0.554 | 0.260 |

Precision decreases more than recall, showing that false detections increase sharply in real scenes. The 0.260 decrease in mAP50-95 also indicates weaker localization under real lighting and material conditions.

| Class | Synthetic AP50 | Real AP50 | Decrease |
|---|---:|---:|---:|
| `pens` | 0.994 | 0.986 | 0.008 |
| `scissors` | 0.995 | 0.922 | 0.073 |
| `tapes` | 0.995 | 0.903 | 0.092 |
| `paper_and_notebooks` | 0.995 | 0.878 | 0.117 |
| `dirt` | 0.908 | 0.773 | 0.135 |
| `business_cards` | 0.995 | 0.852 | 0.143 |
| `keys` | 0.982 | 0.639 | 0.343 |
| `rulers` | 0.860 | 0.490 | 0.370 |
| `usb_sticks` | 0.924 | 0.520 | 0.404 |
| `other` | 0.961 | 0.404 | 0.557 |

## Error Analysis

- `dirt`: approximately 29% of real dirt instances are missed. Floor reflections and texture generate additional false positives.
- `rulers`: thin, transparent, or light-colored rulers generalize poorly on dark floors.
- `usb_sticks`: many instances are missed or confused with `other`.
- `other`: the broad class definition overlaps visually with keys, USB sticks, scissors, and some dirt patterns.
- `keys`: recall is 0.783, but precision is only 0.466 because reflections and unrelated objects are often classified as keys.
- `tapes`: all 24 instances are recalled, but precision is 0.723, indicating extra detections.

Real images contain low illumination, strong reflections, camera noise, floor scratches, and material variation that are not adequately represented in the synthetic training distribution.

## Dirt-Specific Assessment

The `dirt` class achieves 0.852 precision and 0.706 recall. Dirt detections are generally credible, but approximately 29% of ground-truth dirt is missed. Its mAP50 is 0.773 while mAP50-95 is 0.489, a difference of 0.284. Irregular shapes, ambiguous annotation boundaries, and blurred real dirt edges reduce performance at strict IoU thresholds.

The test split contains no background-only images, so it cannot fully measure false-alarm frequency during continuous robot inspection. A lower confidence threshold may improve dirt recall, but it must be validated on clean floors with reflections, shadows, and scratches.

## Inference Performance

| Stage | Time per image |
|---|---:|
| Preprocessing | 1.1 ms |
| Model inference | 30.4 ms |
| Postprocessing | 1.7 ms |
| Total | approximately 33.2 ms |

The measured model pipeline is capable of approximately 30 frames per second. Actual robot throughput will also depend on camera capture, data transfer, visualization, and control logic.

## Comparison with the ICRA 2020 DirtNet Results

The original DirtNet paper reports mAP at IoU 0.5 for its 10-class real test experiment. This is directly comparable with the YOLO11 multiclass mAP50 value, but not with mAP50-95.

| Model | Real-test mAP50 | Difference from YOLO11m |
|---|---:|---:|
| DirtNet-D | 0.807 | +0.070 |
| DirtNet-M | 0.771 | +0.034 |
| YOLO11m multiclass | 0.737 | baseline |

The current model is 3.4 percentage points below the lightweight DirtNet-M model and 7.0 percentage points below DirtNet-D on mAP50.

## Recommendations

1. Collect separate real-image training and validation sets.
2. Add more examples of `rulers`, `usb_sticks`, `keys`, and the visually diverse `other` class.
3. Add difficult negative images containing clean floors, reflections, scratches, and shadows.
4. Expand augmentation for low light, sensor noise, exposure variation, and reflections.
5. Review the definition of `other` and reduce overlap with the named office-item classes.
6. Select deployment thresholds according to the robot's precision and recall requirements.

The 80 test images must not be reused for training or parameter selection. If they are moved into the training data in a future experiment, a new independent real test set will be required.

## Result Artifacts

- [Test summary CSV](../runs/detect/test/yolo11_multiclass_test_real_new_summary.csv)
- [Precision-recall curves](../runs/detect/test/yolo11m_multiclass_e30_i1024_b2_test_real_new/BoxPR_curve.png)
- [F1-confidence curves](../runs/detect/test/yolo11m_multiclass_e30_i1024_b2_test_real_new/BoxF1_curve.png)
- [Normalized confusion matrix](../runs/detect/test/yolo11m_multiclass_e30_i1024_b2_test_real_new/confusion_matrix_normalized.png)
- [Count confusion matrix](../runs/detect/test/yolo11m_multiclass_e30_i1024_b2_test_real_new/confusion_matrix.png)

## Conclusion

The model is a valid first multiclass real-scene baseline, but it is not yet equally reliable across all classes. The dominant problem is the synthetic-to-real domain gap rather than insufficient convergence on synthetic data.

A follow-up [fine-tuning experiment](yolo11_multiclass_finetuning_analysis.md) improved every synthetic validation metric but did not improve overall real-test performance. That result supports retaining this first model as the recommended multiclass baseline.
