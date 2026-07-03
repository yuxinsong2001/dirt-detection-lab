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
→ multi-class architecture validation
→ final model selection
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
- YOLOv8l
- YOLO11l

These models were chosen because they represented the strongest or most relevant candidates from the binary-stage comparison.

The purpose was to re-evaluate these candidates under the actual 10-class multi-class detection setting.

---

## 4. Practical Limitation

The original plan was to validate all three selected models:

```text
YOLOv3u
YOLOv8l
YOLO11l
```

However, due to hardware limitations, YOLOv3u could not be completed under the available local training environment. The YOLOv3u experiment required more GPU memory than available on the current laptop GPU setup, so it was not included in the final numerical comparison.

Therefore, the completed multi-class validation comparison includes:

```text
YOLOv8l
YOLO11l
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

The main metric is **validation mAP50-95**, because it evaluates detection and localization performance across multiple IoU thresholds and is therefore more strict than mAP50 alone.

---

## 6. Completed Model Comparison

### 6.1 YOLOv8l_e30_sgd_aligned

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLOv8l_e30_sgd_aligned | 29 | 0.97198 | 0.92776 | 0.96152 | 0.82417 |

Observation:

YOLOv8l achieved strong precision and stable multi-class detection performance. It produced the highest precision among the completed comparison models, indicating fewer false positive detections.

---

### 6.2 YOLO11l_e30_sgd_aligned

| Model | Best Epoch | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|
| YOLO11l_e30_sgd_aligned | 29 | 0.96432 | 0.93674 | 0.96715 | 0.83170 |

Observation:

YOLO11l achieved higher recall, mAP50, and mAP50-95 than YOLOv8l. Although its precision was slightly lower, its overall detection performance was better according to the main selection metric.

---

## 7. Result Summary

| Model | Best Epoch | Optimizer | Precision | Recall | mAP50 | mAP50-95 | Status |
|---|---:|---|---:|---:|---:|---:|---|
| YOLOv3u_e30_sgd_aligned | - | SGD | - | - | - | - | Not completed due to GPU memory limitation |
| YOLOv8l_e30_sgd_aligned | 29 | SGD | 0.97198 | 0.92776 | 0.96152 | 0.82417 | Completed |
| YOLO11l_e30_sgd_aligned | 29 | SGD | 0.96432 | 0.93674 | 0.96715 | 0.83170 | Completed |

---

## 8. Difference Between YOLO11l and YOLOv8l

The following table shows the difference between YOLO11l and YOLOv8l:

```text
Difference = YOLO11l - YOLOv8l
```

| Metric | Difference | Interpretation |
|---|---:|---|
| Precision | -0.00766 | YOLOv8l has slightly fewer false positives |
| Recall | +0.00898 | YOLO11l detects more true objects |
| mAP50 | +0.00563 | YOLO11l performs slightly better at IoU = 0.5 |
| mAP50-95 | +0.00753 | YOLO11l has better overall detection and localization quality |

The result shows that YOLOv8l is slightly better in precision, but YOLO11l is better in recall, mAP50, and mAP50-95.

Since the main selection criterion is validation mAP50-95, YOLO11l is selected as the better multi-class baseline model among the completed candidates.

---

## 9. Discussion

This validation experiment shows that binary-stage architecture screening is useful, but it is not sufficient for final model selection.

Binary detection is simpler because it does not require distinguishing between detailed object categories. It can be used as a preliminary screening step to identify promising architectures. However, the final application requires multi-class detection, where the model must classify objects into 10 different categories.

Therefore, the selected binary-stage models need to be re-tested on the multi-class task.

In the completed validation, YOLO11l achieved the highest validation mAP50-95. This suggests that the strong performance of YOLO11l in the binary stage can also transfer well to the multi-class task. However, the difference between YOLO11l and YOLOv8l is relatively small, so the conclusion should be stated as:

```text
YOLO11l performed slightly better than YOLOv8l under the completed aligned multi-class validation setting.
```

rather than claiming an absolute advantage in all scenarios.

---

## 10. Main Conclusion

The main conclusions are:

1. Binary detection results should not be directly used as the final multi-class model selection result.
2. The best binary-stage architectures should be validated again on the multi-class task.
3. YOLOv8l and YOLO11l were successfully compared under the multi-class setting.
4. YOLOv3u could not be completed due to local GPU memory limitations.
5. Among the completed validation experiments, YOLO11l achieved the highest validation mAP50-95.
6. Therefore, YOLO11l is selected as the better multi-class baseline model among the completed candidates.

Final conclusion:

```text
YOLO11l_e30_sgd_aligned achieved the best validation mAP50-95 among the completed binary-to-multi-class validation candidates and is therefore selected as the current best multi-class baseline model.
```

---

## 11. Suggested Report Text

The following paragraph can be used in the final report or presentation:

```text
After the binary detection stage, the top candidate architectures were selected for further validation on the 10-class multi-class detection task. This step was necessary because binary detection and multi-class detection have different task definitions. A model that performs well in binary detection does not automatically guarantee the best performance in the multi-class setting.

The selected candidates were YOLOv3u, YOLOv8l, and YOLO11l. Due to local GPU memory limitations, the YOLOv3u experiment could not be completed. Therefore, the final numerical comparison was conducted between YOLOv8l_e30_sgd_aligned and YOLO11l_e30_sgd_aligned.

YOLOv8l achieved a best validation mAP50-95 of 0.82417, while YOLO11l achieved a higher mAP50-95 of 0.83170. Although YOLOv8l had slightly higher precision, YOLO11l achieved better recall, mAP50, and mAP50-95. Since validation mAP50-95 is the main model selection criterion, YOLO11l was selected as the better multi-class baseline model among the completed candidates.
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
