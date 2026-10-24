# YOLO11 Multiclass Fine-Tuning Analysis

This document evaluates a second-stage fine-tuning experiment built on the selected YOLO11m multiclass baseline. The purpose was to determine whether additional optimization on the same synthetic training distribution could improve both synthetic validation performance and generalization to the held-out real-image test split.

## Experiment Design

The fine-tuning run started from the best checkpoint of `yolo11m_multiclass_e30_i1024_b2`, selected at baseline epoch 29.

| Setting | Value |
|---|---|
| Task | 10-class object detection |
| Starting checkpoint | Best baseline checkpoint |
| Additional epochs | 15 |
| Input size | 1024 |
| Batch size | 2 |
| Optimizer | AdamW |
| Learning-rate schedule | cosine |
| Patience | 5 |
| AMP | enabled |
| Training distribution | same synthetic train and validation splits as the baseline |

The complete effective settings are stored in [`args.yaml`](../../runs/detect/training/yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2/args.yaml).

## Synthetic Validation Results

The best fine-tuning result occurred at additional epoch 13.

| Metric | Baseline best | Fine-tuned best | Change |
|---|---:|---:|---:|
| Precision | 0.9535 | 0.9674 | +0.0139 |
| Recall | 0.9305 | 0.9438 | +0.0133 |
| mAP50 | 0.9608 | 0.9679 | +0.0071 |
| mAP50-95 | 0.8136 | 0.8259 | +0.0123 |

All four synthetic validation metrics improved. The additional training therefore optimized the model more closely for the synthetic data distribution.

## Held-Out Real-Test Results

The fine-tuned checkpoint was re-evaluated on all 80 real test images with 644 labeled instances.

| Metric | Baseline | Fine-tuned | Change |
|---|---:|---:|---:|
| Precision | 0.665 | 0.726 | +0.061 |
| Recall | 0.776 | 0.721 | -0.055 |
| mAP50 | 0.737 | 0.726 | -0.011 |
| mAP50-95 | 0.554 | 0.557 | +0.003 |

The precision increase is offset by a substantial recall decrease. Real-test mAP50 declines by 1.1 percentage points, while mAP50-95 changes by only 0.3 percentage points. This is not a meaningful overall generalization improvement.

## Per-Class Real-Test Comparison

| Class | Baseline mAP50 | Fine-tuned mAP50 | Change |
|---|---:|---:|---:|
| `dirt` | 0.773 | 0.774 | +0.001 |
| `business_cards` | 0.852 | 0.860 | +0.008 |
| `keys` | 0.639 | 0.592 | -0.047 |
| `other` | 0.404 | 0.358 | -0.046 |
| `paper_and_notebooks` | 0.878 | 0.853 | -0.025 |
| `pens` | 0.986 | 0.991 | +0.005 |
| `rulers` | 0.490 | 0.419 | -0.071 |
| `scissors` | 0.922 | 0.925 | +0.003 |
| `tapes` | 0.903 | 0.847 | -0.056 |
| `usb_sticks` | 0.520 | 0.640 | +0.120 |

The fine-tuned model improves `usb_sticks`, but several classes degrade, especially `rulers`, `tapes`, `keys`, and `other`. The aggregate result remains worse at IoU 0.5.

## Interpretation

The experiment shows a clear divergence between synthetic validation and real-image performance:

- synthetic precision, recall, mAP50, and mAP50-95 all improve;
- real-test recall and mAP50 decline;
- real-test mAP50-95 is effectively unchanged; and
- class-level gains are inconsistent and are offset by degradation in several difficult classes.

This pattern indicates overfitting to the synthetic distribution. Because the optimizer and learning-rate schedule were also changed, the experiment does not isolate training duration as the only cause. It does show that further optimization on the existing synthetic data is not the correct path to better real-scene performance.

The baseline model had already learned the useful information available in the current synthetic dataset. Its lower synthetic validation score does not indicate an undertrained model; instead, it offers a slightly better balance on the independent real test set.

## Conclusion

The original `yolo11m_multiclass_e30_i1024_b2` checkpoint remains the recommended multiclass baseline. The second-stage fine-tuning run provides additional experimental evidence that the main remaining limitation is the synthetic-to-real domain gap rather than insufficient synthetic training.

Future improvements should prioritize real-domain training and validation images, difficult negative examples, and clearer class definitions instead of additional fine-tuning on the same synthetic split.

## Result Artifacts

- [Fine-tuning metrics](../../runs/detect/training/yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2/results.csv)
- [Fine-tuning curves](../../runs/detect/training/yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2/results.png)
- [Fine-tuning precision-recall curves](../../runs/detect/training/yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2/BoxPR_curve.png)
- [Real-test summary CSV](../../runs/detect/test/yolo11_multiclass_test_real_new_summary.csv)
- [Fine-tuned real-test precision-recall curves](../../runs/detect/test/yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2_test_real_new/BoxPR_curve.png)
- [Fine-tuned real-test normalized confusion matrix](../../runs/detect/test/yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2_test_real_new/confusion_matrix_normalized.png)
