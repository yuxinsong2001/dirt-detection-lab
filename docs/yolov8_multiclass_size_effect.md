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
Does increasing the YOLOv8 model size improve the multi-class detection result on our dataset?
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
| Image size | 1024 × 1024 |

Because the dataset is relatively small for training larger object detection models, increasing model size may not always lead to better validation performance.

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

Observed result:

| Model | Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8s | 30 | 0.94336 | 0.91745 | 0.94842 | 0.79568 |

Observation:

YOLOv8s showed a clear improvement over YOLOv8n. The increase from YOLOv8n to YOLOv8s improved precision, recall, mAP50, and mAP50-95.

This suggests that increasing the model size from nano to small provides more useful representation capacity for the multi-class detection task.

---

### 4.3 YOLOv8m

YOLOv8m is the medium version of YOLOv8. It has more parameters than YOLOv8s and theoretically has higher model capacity. However, larger capacity does not always lead to better validation performance, especially when the dataset is relatively small or the training configuration is not optimal.

Observed result:

| Model | Best Observed Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8m | 12 | 0.89023 | 0.89262 | 0.92166 | 0.74637 |

Observation:

In the observed result, YOLOv8m did not outperform YOLOv8s. This shows that the relationship between model size and performance is not strictly linear.

Possible reasons include:

- the dataset is relatively small
- the training configuration may not be equally suitable for all model sizes
- YOLOv8m may require more careful learning rate or augmentation tuning
- if training was not completed to the same number of epochs, the result should be treated as an intermediate result
- larger models may be more sensitive to overfitting or unstable optimization on small datasets

---

## 5. Result Summary

| Model | Model Scale | Best / Observed Epoch | Precision | Recall | mAP50 | mAP50-95 | Interpretation |
|---|---|---:|---:|---:|---:|---:|---|
| YOLOv8n | Nano | 28 | 0.88462 | 0.81762 | 0.87501 | 0.71009 | Fastest but lowest accuracy |
| YOLOv8s | Small | 30 | 0.94336 | 0.91745 | 0.94842 | 0.79568 | Strong improvement over YOLOv8n |
| YOLOv8m | Medium | 12 | 0.89023 | 0.89262 | 0.92166 | 0.74637 | Did not outperform YOLOv8s in the observed result |

---

## 6. Model Size Influence Analysis

The comparison shows that model size does affect the output result, but the effect is not simply monotonic.

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

The observed YOLOv8m result was lower than YOLOv8s:

| Metric | YOLOv8s | YOLOv8m | Difference |
|---|---:|---:|---:|
| Precision | 0.94336 | 0.89023 | -0.05313 |
| Recall | 0.91745 | 0.89262 | -0.02483 |
| mAP50 | 0.94842 | 0.92166 | -0.02676 |
| mAP50-95 | 0.79568 | 0.74637 | -0.04931 |

This suggests that simply increasing the model size does not guarantee a better result. YOLOv8m may need more suitable training settings or more training data to fully benefit from its larger capacity.

---

## 7. Main Conclusion

The experiment supports the following conclusion:

```text
Model size has an influence on multi-class detection performance, but the effect is not strictly linear.
```

A moderate increase in model size from YOLOv8n to YOLOv8s clearly improved the result. However, YOLOv8m did not outperform YOLOv8s in the observed experiment, which shows that larger models are not automatically better.

The final performance depends on the combination of:

```text
model size + dataset size + training configuration + optimization stability
```

Therefore, the model should be selected based on validation performance under the tested setting, rather than only based on model size.

---

## 8. Suggested Report Text

The following paragraph can be used in the final report or presentation:

```text
To analyze the influence of model size, YOLOv8n, YOLOv8s, and YOLOv8m were evaluated on the 10-class multi-class dirt/object detection task. The results show that model size affects detection performance, but the relationship is not strictly linear. YOLOv8s achieved a clear improvement over YOLOv8n, especially in recall and mAP50-95, indicating that the nano model was too limited for this task. However, YOLOv8m did not outperform YOLOv8s in the observed experiment. This suggests that larger model capacity does not automatically lead to better validation performance, especially with a relatively small dataset. Therefore, the final model selection should be based on validation mAP50-95 under the tested configuration instead of model size alone.
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

This comparison should be interpreted as a **model size effect analysis** within the YOLOv8 family. It should not be mixed with the later cross-version architecture comparison between models such as YOLOv3u, YOLOv8l, and YOLO11l.

The purpose of this document is to support the overall model selection process by showing that model size can influence performance, but it is not the only determining factor.
