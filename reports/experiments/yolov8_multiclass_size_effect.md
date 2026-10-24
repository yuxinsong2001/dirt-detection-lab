# YOLOv8 Model Size Effect on Multi-class Detection

## 1. Purpose

This document summarizes a supporting analysis for the overall framework selection process in the dirt/object detection project.

The purpose of this experiment is to analyze whether the **model size within the YOLOv8 family** affects the performance of the multi-class detection task on our dataset, and what kind of influence it has.

Compared models:

- YOLOv8n
- YOLOv8s
- YOLOv8m

This comparison is not an independent final model selection experiment. Instead, it provides evidence for understanding how model scale influences detection performance and supports later architecture selection decisions.

Main question:

```text
How does YOLOv8 model size affect the multi-class detection result on our dataset?
```

Main evaluation metric:

```text
validation mAP50-95
```

mAP50-95 is used as the main metric because it evaluates detection and localization quality across multiple IoU thresholds.

---

## 2. Task Description

The task is **multi-class object detection**.

The model needs to predict:

1. the location of each object using bounding boxes
2. the class of each object among 10 categories

The 10 target classes are:

```text
dirt
business_cards
keys
other
paper_and_notebooks
pens
rulers
scissors
tapes
usb_sticks
```

This task is more difficult than binary detection because the model must not only detect whether an object exists, but also distinguish between different object categories.

---

## 3. Dataset Context

The experiment was performed on the multi-class YOLO detection dataset used in this project.

General dataset setting:

| Item | Value |
|---|---:|
| Training images | approximately 860 |
| Validation images | 296 |
| Number of classes | 10 |
| Image size | 1024 x 1024 |

Because the dataset contains 10 object categories and includes small objects, the task requires enough model capacity to learn both localization and class-level differences.

---

## 4. Compared YOLOv8 Model Sizes

### 4.1 YOLOv8n

YOLOv8n is the nano version of YOLOv8. It has the smallest model capacity among the compared models and is expected to be the fastest, but its detection accuracy may be limited.

Best validation result:

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8n | 28 | 0.88462 | 0.81762 | 0.87501 | 0.71009 |

Final epoch result:

| Model | Final Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8n | 30 | 0.87834 | 0.81129 | 0.87247 | 0.70576 |

Observation:

YOLOv8n was able to learn the task, but its recall and mAP50-95 were clearly lower than the larger YOLOv8 models. This indicates that the nano model may not have enough capacity for stable 10-class detection on this dataset.

---

### 4.2 YOLOv8s

YOLOv8s is the small version of YOLOv8. It has higher capacity than YOLOv8n while still remaining relatively lightweight.

Best validation result:

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8s | 30 | 0.94336 | 0.91745 | 0.94842 | 0.79568 |

Observation:

YOLOv8s showed a clear improvement over YOLOv8n. The increase from YOLOv8n to YOLOv8s improved precision, recall, mAP50, and mAP50-95.

This suggests that increasing the model size from nano to small provides more useful representation capacity for the multi-class detection task.

---

### 4.3 YOLOv8m

YOLOv8m is the medium version of YOLOv8. It has more parameters than YOLOv8s and theoretically has higher model capacity.

Best validation result:

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8m | 30 | 0.95863 | 0.93536 | 0.95049 | 0.81288 |

Observation:

After correcting the previous YOLOv8m result, YOLOv8m achieved the best performance among the three tested YOLOv8 scales. It improved over YOLOv8s in precision, recall, mAP50, and mAP50-95, although the improvement from YOLOv8s to YOLOv8m was smaller than the improvement from YOLOv8n to YOLOv8s.

This indicates that a larger YOLOv8 model can provide better multi-class detection performance on this dataset, but the additional gain becomes more moderate as model size increases.

---

## 5. Result Summary

| Model | Model Scale | Best Epoch | Precision | Recall | mAP50 | mAP50-95 | Training Time | Interpretation |
|---|---|---:|---:|---:|---:|---:|---:|---|
| YOLOv8n | Nano | 28 | 0.88462 | 0.81762 | 0.87501 | 0.71009 | 11.6 min | Fastest but lowest accuracy |
| YOLOv8s | Small | 30 | 0.94336 | 0.91745 | 0.94842 | 0.79568 | 78.6 min | Strong improvement over YOLOv8n |
| YOLOv8m | Medium | 30 | 0.95863 | 0.93536 | 0.95049 | 0.81288 | 169.7 min | Best accuracy among tested scales |

---

## 6. Model Size Influence Analysis

The comparison shows that model size has a clear influence on the multi-class detection result within the tested YOLOv8 scales.

### 6.1 From YOLOv8n to YOLOv8s

The performance improved significantly:

| Metric | YOLOv8n | YOLOv8s | Difference |
|---|---:|---:|---:|
| Precision | 0.88462 | 0.94336 | +0.05874 |
| Recall | 0.81762 | 0.91745 | +0.09983 |
| mAP50 | 0.87501 | 0.94842 | +0.07341 |
| mAP50-95 | 0.71009 | 0.79568 | +0.08559 |

This indicates that the nano model is likely too small for this 10-class detection task, while the small model provides more useful feature representation capacity.

### 6.2 From YOLOv8s to YOLOv8m

YOLOv8m further improved over YOLOv8s:

| Metric | YOLOv8s | YOLOv8m | Difference |
|---|---:|---:|---:|
| Precision | 0.94336 | 0.95863 | +0.01527 |
| Recall | 0.91745 | 0.93536 | +0.01791 |
| mAP50 | 0.94842 | 0.95049 | +0.00207 |
| mAP50-95 | 0.79568 | 0.81288 | +0.01720 |

The improvement from YOLOv8s to YOLOv8m is smaller than the improvement from YOLOv8n to YOLOv8s, but it is still consistent across the main metrics.

### 6.3 Accuracy and training-cost trade-off

The larger model also required more training time:

| Model | Training Time |
|---|---:|
| YOLOv8n | 11.6 min |
| YOLOv8s | 78.6 min |
| YOLOv8m | 169.7 min |

This shows a practical trade-off: larger models improved detection accuracy, but they also required higher training cost. Therefore, model size should be considered together with available GPU resources and project requirements.

---

## 7. Main Conclusion

The experiment supports the following conclusion:

```text
Within the tested YOLOv8 scales, larger models achieved better multi-class detection performance.
```

The nano model was clearly weaker than the small and medium models. YOLOv8s provided a large improvement over YOLOv8n, and YOLOv8m achieved the best overall validation performance among the tested scales.

Therefore, the result suggests that relatively larger YOLOv8 models are more suitable for this project than the nano scale. However, the accuracy gain comes with a clear increase in training time, so the final model choice should also consider computational cost.

This experiment should be interpreted as a **model-size effect analysis**, not as the final architecture selection for the whole project.

---

## 8. Suggested Report Text

The following paragraph can be used in the final report or presentation:

```text
To analyze the influence of model size, YOLOv8n, YOLOv8s, and YOLOv8m were evaluated on the 10-class multi-class dirt/object detection task. The results show that model size has a clear effect on detection performance. YOLOv8n achieved the lowest mAP50-95, while YOLOv8s and YOLOv8m produced much stronger results. YOLOv8m achieved the best validation performance among the tested scales, with mAP50-95 increasing from 0.71009 for YOLOv8n to 0.79568 for YOLOv8s and 0.81288 for YOLOv8m. This suggests that relatively larger models are more suitable for this project than the nano scale. At the same time, the training time increased significantly with model size, so the final model choice should also consider computational cost and available GPU resources.
```

---

## 9. Recommended Repository Location

This document is a supporting analysis for the overall framework selection process. Therefore, the recommended repository location is:

```text
docs/yolov8_multiclass_size_effect.md
```

If raw result files are uploaded later, they should follow the existing repository structure agreed by the team. This document only summarizes and interprets the key model-size comparison results.

---

## 10. Notes

This comparison should be interpreted as a **model size effect analysis** within the YOLOv8 family. It should not be mixed with the later cross-version architecture comparison between models such as YOLOv3u, YOLOv8l, YOLOv5lu, and YOLO11l.

The purpose of this document is to support the overall model selection process by showing that model size can influence performance. The corrected result indicates that, under this tested setting, larger YOLOv8 scales led to better multi-class detection performance, while also increasing training cost.
