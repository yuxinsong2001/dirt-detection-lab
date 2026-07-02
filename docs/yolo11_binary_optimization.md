# YOLO11 Binary Detection Optimization Summary

This document summarizes the current YOLO11 optimization logic for the binary DirtNet reproduction task. The goal is to select a final 2-class detector using the full binary dataset.

## Current Setup

- Dataset config: `binary_full.yaml`
- Dataset split: full binary dataset
- Task: 2-class object detection
- Input size: `imgsz=1024`
- Batch size: `batch=8`
- Main validation source: `images/val`
- Main metric: mAP50
- Secondary metrics: precision, recall, mAP50-95, training time

## 1. Model Size Screening

The first step after selecting YOLO11 was to compare different model sizes under the same basic setting.

| Experiment | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|
| `yolo11n_full_default_e15_b8` | 0.927 | 0.886 | 0.929 | 0.785 | 1292.8s |
| `yolo11s_full_default_e15_b8` | 0.950 | 0.917 | 0.956 | 0.834 | 2059.2s |
| `yolo11m_full_default_e15_b8` | 0.949 | 0.926 | 0.962 | 0.854 | 4160.8s |

The n model is much faster, but its mAP50 is clearly lower. The s and m models are closer in mAP50, while m takes about twice as long as s.

Based on this result, the current strategy is:

- Use YOLO11s for parameter screening.
- Avoid spending long training time on YOLO11m before the parameter direction is clear.
- After a stable YOLO11s setting is selected, apply the same setting to YOLO11m for the final size comparison.

## 2. Optimizer Choice

The current results show that SGD is a good optimizer choice for this dataset.

| Experiment | Optimizer | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---|---:|---:|---:|---:|---:|
| `yolo11s_full_default_e15_b8` | auto | 0.950 | 0.917 | 0.956 | 0.834 | 2059.2s |
| `yolo11s_full_sgd_e15_b8` | SGD | 0.963 | 0.923 | 0.959 | 0.844 | 2096.9s |
| `yolo11m_full_default_e15_b8` | auto | 0.949 | 0.926 | 0.962 | 0.854 | 4160.8s |
| `yolo11m_full_sgd_e15_b8` | SGD | 0.965 | 0.939 | 0.971 | 0.875 | 4114.2s |

SGD improves the current mAP50 result on both YOLO11s and YOLO11m. It also improves recall and mAP50-95.

For this stage, there is no need to separately list the SGD learning-rate and momentum values in every command. They match the YOLO default values when `optimizer=SGD` is selected.

There is also no strong reason to add a manual AdamW run right now. The `optimizer=auto` setting already selects an AdamW-style path for these short runs and handles its own learning-rate choice. A manual AdamW command would mainly become an extra learning-rate tuning experiment, not a clean comparison.

Current decision:

- Keep `optimizer=SGD` as the main setting.
- Keep `optimizer=auto` only as a baseline reference.
- Do not prioritize manual AdamW tuning unless SGD later becomes unstable or clearly plateaus.

## 3. Augmentation Setting

After choosing YOLO11s for parameter screening, one test compared the normal SGD setting with an aligned augmentation setting. The meaningful changed items were:

- `auto_augment=none`
- `erasing=0.0`

Other items in the command, such as `mosaic=1.0` and `mixup=0.0`, are already consistent with the default detection setting, so they are not treated as separate changes here.

| Experiment | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_e15_b8` | 0.963 | 0.923 | 0.959 | 0.844 | 2096.9s |
| `yolo11s_full_sgd_aligned_aug_e15_b8` | 0.963 | 0.923 | 0.959 | 0.844 | 2067.6s |

The result is essentially unchanged. This suggests that the tested augmentation changes are not the source of the improvement seen in later experiments.

Current decision:

- Use default detection augmentation.
- Do not add extra augmentation parameters unless there is a specific hypothesis.

## 4. AMP Setting

During the augmentation comparison, an additional run disabled AMP. This was useful because it separated augmentation effects from the training-cost effect of full precision.

| Experiment | AMP | Precision | Recall | mAP50 | mAP50-95 | Time |
|---|---:|---:|---:|---:|---:|---:|
| `yolo11s_full_sgd_aligned_aug_e15_b8` | true | 0.963 | 0.923 | 0.959 | 0.844 | 2067.6s |
| `yolo11s_full_sgd_aligned_aug_amp_false_e15_b8` | false | 0.960 | 0.922 | 0.960 | 0.847 | 3278.8s |

The run with `amp=False` takes much longer, while mAP50 stays almost unchanged. Its time cost moves YOLO11s closer to the cost level of a larger model, but it does not provide a comparable accuracy gain.

Current decision:

- Keep AMP enabled.
- Do not use `amp=False` as an optimization direction.

## 5. Current Conclusion

The current optimization logic is:

1. YOLO11n is too weak for the current target.
2. YOLO11s is the best model for parameter screening because it is close to YOLO11m in mAP50 but much faster.
3. YOLO11m should be used after the YOLO11s setting is selected, mainly to check whether the larger model gives enough final gain.
4. Default detection augmentation is enough.
5. `amp=False` is not worth using.
6. `optimizer=SGD` is the current main optimizer choice.

The next main experiment should therefore be a longer YOLO11s SGD run, judged primarily by mAP50.
