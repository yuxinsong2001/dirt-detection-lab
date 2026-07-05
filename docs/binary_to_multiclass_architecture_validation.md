# Binary-to-Multi-class Architecture Validation

## 1. Purpose

This document summarizes a validation experiment that connects the binary detection experiments with the multi-class detection task.

In the earlier stage of the project, multiple YOLO architectures were compared on the binary detection task. The purpose of that binary experiment was to perform an initial architecture screening under a simpler task setting.

However, the final project target is **multi-class dirt/object detection**, not only binary detection. Therefore, the architectures that performed well in the binary task need to be verified again on the 10-class multi-class detection task.

The main question of this validation experiment is:

```text
Do the architectures that perform well in binary detection also work well for the multi-class detection task?
```

This experiment is used as a bridge between:

```text
binary architecture screening
-> multi-class architecture validation
-> final model selection
```

---

## 2. Background

The binary detection task and the multi-class detection task have different purposes.

In binary detection, the model only needs to decide whether a target object exists. Different object categories are usually merged into one general class.

In multi-class detection, the model must detect the object location and classify each object into one of the 10 target categories.

Therefore, binary results cannot be directly treated as final evidence for the multi-class model selection. A model that performs well in binary detection may not necessarily be the best model for multi-class detection, because the multi-class task includes additional class discrimination difficulty.

---

## 3. Candidate Architectures from Binary Screening

Based on the previous binary architecture comparison, the selected candidate models for multi-class validation were:

- YOLOv3u
- YOLOv5LU
- YOLOv8L
- YOLO11L

These models were chosen because they represented the strongest or most relevant candidates from the binary-stage comparison.

The purpose was to re-evaluate these candidates under the actual 10-class multi-class detection setting and check whether the binary-stage ranking could still support the multi-class model selection.

---

## 4. Practical Limitation

The original plan was to validate all selected candidates:

```text
YOLOv3u
YOLOv5LU
YOLOv8L
YOLO11L
```

However, due to hardware limitations, YOLOv3u could not be completed under the available local training environment. The YOLOv3u experiment required more GPU memory than available on the current laptop GPU setup, so it was not included in the final numerical comparison.

Therefore, the completed multi-class validation comparison includes:

```text
YOLOv5LU
YOLOv8L
YOLO11L
```

This limitation should be clearly mentioned in the report to avoid giving the impression that YOLOv3u was intentionally excluded.

---

## 5. Multi-class Validation Setting

The validation was conducted on the 10-class multi-class detection task.

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

The compared models were trained under aligned baseline settings as much as possible.

Typical aligned setting:

| Parameter | Value |
|---|---|
| Task | Multi-class object detection |
| Number of classes | 10 |
| Epochs | 30 |
| Optimizer | SGD |
| Image size | 1024 |
| Batch size | 2 |
| Main selection metric | validation mAP50-95 |

Important fixed settings:

```text
imgsz=1024
batch=2
epochs=30
optimizer=SGD
lr0=0.01
lrf=0.01
mosaic=1.0
mixup=0.0
erasing=0.0
auto_augment=none
amp=False
```

The main metric is **validation mAP50-95**, because it evaluates detection and localization performance across multiple IoU thresholds and is therefore more strict than mAP50 alone.

---

## 6. Completed Model Comparison

### 6.1 YOLOv5LU

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 | Training Time |
|---|---:|---:|---:|---:|---:|---:|
| YOLOv5LU | 30 | 0.96439 | 0.93563 | 0.96360 | 0.82001 | 132.0 min |

Observation:

YOLOv5LU achieved strong multi-class detection performance and was close to the other large-scale candidates. However, its mAP50-95 was lower than YOLOv8L and YOLO11L, and its training time was the longest among the completed models.

---

### 6.2 YOLOv8L

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 | Training Time |
|---|---:|---:|---:|---:|---:|---:|
| YOLOv8L | 29 | 0.97198 | 0.92776 | 0.96152 | 0.82417 | 97.4 min |

Observation:

YOLOv8L achieved the highest precision among the completed comparison models, indicating fewer false positive detections. However, its recall, mAP50, and mAP50-95 were lower than YOLO11L.

---

### 6.3 YOLO11L

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 | Training Time |
|---|---:|---:|---:|---:|---:|---:|
| YOLO11L | 29 | 0.96432 | 0.93674 | 0.96715 | 0.83170 | 91.5 min |

Observation:

YOLO11L achieved the highest recall, mAP50, and mAP50-95 among the completed candidates. It also had the shortest training time in this comparison. Although its precision was slightly lower than YOLOv8L, it showed the best overall balance across the key multi-class validation metrics.

---

## 7. Result Summary

| Model | Best Epoch | Optimizer | Precision | Recall | mAP50 | mAP50-95 | Training Time | Status |
|---|---:|---|---:|---:|---:|---:|---:|---|
| YOLOv3u_e30_sgd_aligned | - | SGD | - | - | - | - | - | Not completed due to GPU memory limitation |
| YOLOv5LU | 30 | SGD | 0.96439 | 0.93563 | 0.96360 | 0.82001 | 132.0 min | Completed |
| YOLOv8L | 29 | SGD | 0.97198 | 0.92776 | 0.96152 | 0.82417 | 97.4 min | Completed |
| YOLO11L | 29 | SGD | 0.96432 | 0.93674 | 0.96715 | 0.83170 | 91.5 min | Completed |

---

## 8. Comparison Against YOLO11L

The following table shows the difference between YOLO11L and the other completed candidates:

```text
Difference = YOLO11L - compared model
```

| Compared Model | Precision | Recall | mAP50 | mAP50-95 | Training Time | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| YOLOv5LU | -0.00007 | +0.00111 | +0.00355 | +0.01169 | -40.5 min | YOLO11L is slightly better in recall and mAP, and much faster |
| YOLOv8L | -0.00766 | +0.00898 | +0.00563 | +0.00753 | -5.9 min | YOLOv8L has higher precision, but YOLO11L is better in recall, mAP, and time |

The result shows that YOLO11L is not dramatically ahead in every single metric, but it is the most consistent candidate across the key selection factors:

- highest recall
- highest mAP50
- highest mAP50-95
- shortest training time among the completed candidates

Since the main selection criterion is validation mAP50-95, and since training cost is also relevant for the project, YOLO11L is selected as the better multi-class baseline model among the completed candidates.

---

## 9. Discussion

This validation experiment shows that binary-stage architecture screening is useful, but it is not sufficient for final model selection.

Binary detection is simpler because it does not require distinguishing between detailed object categories. It can be used as a preliminary screening step to identify promising architectures. However, the final application requires multi-class detection, where the model must classify objects into 10 different categories.

Therefore, the selected binary-stage models need to be re-tested on the multi-class task.

In the completed validation, YOLO11L achieved the highest validation mAP50-95. YOLOv8L achieved the highest precision, and YOLOv5LU also produced competitive results. However, YOLO11L showed the best overall balance because it had the highest recall, mAP50, mAP50-95, and the shortest training time.

The conclusion should therefore be stated as:

```text
YOLO11L showed the best overall balance among the completed aligned multi-class validation candidates.
```

rather than claiming an absolute advantage in every possible scenario.

---

## 10. Main Conclusion

The main conclusions are:

1. Binary detection results should not be directly used as the final multi-class model selection result.
2. The best binary-stage architectures should be validated again on the multi-class task.
3. YOLOv5LU, YOLOv8L, and YOLO11L were successfully compared under the multi-class setting.
4. YOLOv3u could not be completed due to local GPU memory limitations.
5. YOLO11L achieved the highest validation mAP50-95 among the completed candidates.
6. YOLO11L also achieved the highest recall, highest mAP50, and shortest training time.
7. Therefore, YOLO11L is selected as the most suitable multi-class baseline model among the completed candidates.

Final conclusion:

```text
YOLO11L achieved the best overall balance among the completed binary-to-multi-class validation candidates and is therefore selected as the current multi-class baseline model for further optimization.
```

---

## 11. Suggested Report Text

The following paragraph can be used in the final report or presentation:

```text
After the binary detection stage, the top candidate architectures were selected for further validation on the 10-class multi-class detection task. This step was necessary because binary detection and multi-class detection have different task definitions. A model that performs well in binary detection does not automatically guarantee the best performance in the multi-class setting.

The selected candidates were YOLOv3u, YOLOv5LU, YOLOv8L, and YOLO11L. Due to local GPU memory limitations, the YOLOv3u experiment could not be completed. Therefore, the final numerical comparison was conducted among YOLOv5LU, YOLOv8L, and YOLO11L under aligned multi-class settings.

YOLOv5LU achieved a best validation mAP50-95 of 0.82001, YOLOv8L achieved 0.82417, and YOLO11L achieved the highest mAP50-95 of 0.83170. YOLOv8L had the highest precision, but YOLO11L achieved the highest recall, mAP50, mAP50-95, and the shortest training time among the completed candidates. Therefore, YOLO11L was selected as the most suitable multi-class baseline model for further optimization.
```

---

## 12. Recommended Repository Location

This document is part of the overall model selection documentation and can be placed under the existing documentation folder:

```text
docs/binary_to_multiclass_architecture_validation.md
```

If raw result files are uploaded later, they should follow the existing repository structure agreed by the team. This document only summarizes and interprets the key validation results.

---

## 13. Notes

This document should be interpreted as a **cross-task validation summary**.

It is different from:

- YOLOv8 N/S/M model size effect analysis
- binary-only optimization results
- final demo inference documentation

Its specific role is to explain how the binary-stage architecture screening was connected to the multi-class model selection process.
