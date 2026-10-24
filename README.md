# Vision-Based Dirt Detection for Cleaning Robots

Start with [the repository navigation guide](START_HERE.md) to locate code,
experiment records, reports and generated analysis outputs. Personal bilingual
learning notes remain local and are not part of the GitHub deliverables.

## Project Overview

This course project reproduces and extends the vision-based floor dirt detection
approach introduced by DirtNet. It compares multiple YOLO generations, selects
Ultralytics YOLO11 for the final implementation, and studies model size, training
settings, synthetic validation performance, and generalization to real images.
The repository covers two object-detection tasks:

- Binary detection: `dirt` and `object`
- Multiclass extension: dirt and nine office-object classes

The main experiments use YOLO11s and YOLO11m. Training data, test images, and model
weights are not stored in Git because of their size. The repository keeps dataset
layouts, configuration files, experiment metadata, metrics, and documentation so
the experiments can be reproduced locally.

## Team

| Name | Student ID |
|---|---:|
| Shufang Tao | 3824652 |
| Yuxin Song | 3820779 |
| Yuyang Ren | 3762594 |

## Repository Layout

```text
.
|-- binary_full.yaml                 # Binary dataset configuration
|-- multiclass_small.yaml            # Ten-class dataset configuration
|-- dataset_convert_to_yolo_binary.py # Compatibility launcher
|-- datasets/                         # Local datasets; only layout READMEs are tracked
|-- docs/                             # Setup and execution guides
|-- runs/                             # Tracked metrics and plots; weights are ignored
|-- scripts/                          # Original project utility implementations
|-- tools/                            # Compatibility launchers for old commands
|-- experiment-analysis/              # New analysis tools, tests, outputs and local learning notes
|-- reports/                          # PDF reports, presentations and analysis outputs
|-- logs/                             # Runtime text logs (ignored)
|-- archive/                          # Preserved source downloads
|-- weights/                          # Pretrained and trained .pt files; ignored by Git
`-- requirements.txt
```

Run all commands below from the repository root.

The repository has two related parts: the original YOLO experiments and the
self-contained [experiment analysis module](experiment-analysis/README.md).
See [the layout and maintenance policy](docs/repository-layout.md) for stable
data paths, archived outputs and compatibility entry points.

## Environment

The experiments were run on Windows with Conda. The binary experiments used a
desktop NVIDIA RTX 4070. The formal multiclass experiments used an NVIDIA RTX 3060
Laptop GPU with 6 GB VRAM.

```powershell
conda create -n dirtnet python=3.12 -y
conda activate dirtnet
pip install -r requirements.txt
yolo checks
```

The requirements file contains only the dependencies used directly by this
repository. Ultralytics installs its runtime stack, including PyTorch and OpenCV.
PyYAML is listed explicitly because the configuration utility imports it directly.
The historical PDF generator has optional dependencies:

```powershell
pip install -r requirements-reporting.txt
```

ReportLab is not needed for training or the experiment inventory. The existing
local `.venv` currently imports Ultralytics from the nested `ultralytics-repo`
checkout; moving that checkout would break that environment. A fresh installation
may instead use the package installed by pip. Do not recreate the existing virtual
environment merely to tidy the folder list.

When a specific CUDA-enabled PyTorch build is required, install that build first
for the local GPU and then run the requirements command above.

The recorded multiclass environment used Python 3.12.10, PyTorch 2.12.1+cu130,
and Ultralytics 8.4.74. Exact PyTorch and CUDA builds may be adapted to the local
GPU and driver.

## Dataset Setup

**Local setup note:** the root YAML files describe the shared `datasets/` layout,
but those train/validation/test directories are not populated on this machine.
The existing local data are under `data/`. Use the ignored `cfg/local/` YAMLs for
those data, following [the local-path guide](docs/local-data-paths.md). Replace the
`data=` argument with the appropriate local YAML; do not assume that the local
small dataset is interchangeable with the documented full dataset.

### Binary Dataset

The expected converted layout is documented in
[`datasets/binary/full/README.md`](datasets/binary/full/README.md). The root-level
[`binary_full.yaml`](binary_full.yaml) uses these splits:

```text
datasets/binary/full/
|-- images/train
|-- images/val
|-- images/test_real_new
|-- labels/train
|-- labels/val
`-- labels/test_real_new
```

To convert the original DirtNet-style source data into the binary YOLO format,
place the source files under `datasets/images/` as described by the converter and
run:

```powershell
python scripts/dataset_convert_to_yolo_binary.py --profile full
```

Use `--clear` only when the existing converted output should be regenerated:

```powershell
python scripts/dataset_convert_to_yolo_binary.py --profile full --clear
```

The converter maps dirt to class 0 and all office objects to class 1. Synthetic
floor IDs 0-15 form the training split and IDs 16-20 form the validation split.

### Multiclass Dataset

The ten-class layout is documented in
[`datasets/multiclass/small/README.md`](datasets/multiclass/small/README.md). Its
configuration is [`multiclass_small.yaml`](multiclass_small.yaml), with the
following classes:

```text
dirt, business_cards, keys, other, paper_and_notebooks,
pens, rulers, scissors, tapes, usb_sticks
```

## Pretrained Weights

Place the official Ultralytics checkpoints in `weights/`:

```text
weights/yolo11s.pt
weights/yolo11m.pt
```

Alternatively, replace `weights/yolo11s.pt` or `weights/yolo11m.pt` in a command
with `yolo11s.pt` or `yolo11m.pt` and let Ultralytics download the checkpoint.

The current `weights/` directory is empty and not every historical run retains its
checkpoint. Commands below are reproduction recipes, not a claim that all required
data and trained weights already exist locally. Do not regenerate anything merely
to validate repository organization.

## Reproduce Binary Training

The final binary comparison uses SGD, 1280-pixel input, and 30 epochs:

```powershell
yolo detect train model=weights/yolo11s.pt data=binary_full.yaml imgsz=1280 batch=8 epochs=30 optimizer=SGD name=yolo11s_final_img1280_sgd_e30_b8 project=runs/detect/training
```

```powershell
yolo detect train model=weights/yolo11m.pt data=binary_full.yaml imgsz=1280 batch=4 epochs=30 optimizer=SGD name=yolo11m_final_img1280_sgd_e30_b4 project=runs/detect/training
```

Batch size 4 is used for YOLO11m because the 1280-pixel batch-8 configuration
exceeded the available GPU memory. Ultralytics validates on the `val` split during
training and saves outputs under `runs/detect/training/<name>/`.

## Reproduce Multiclass Training

Train the YOLO11m multiclass baseline:

```powershell
yolo detect train model=weights/yolo11m.pt data=multiclass_small.yaml imgsz=1024 batch=2 epochs=30 workers=0 name=yolo11m_multiclass_e30_i1024_b2 project=runs/detect/training
```

Fine-tune the best baseline checkpoint with the tested conservative schedule:

```powershell
yolo detect train model=runs/detect/training/yolo11m_multiclass_e30_i1024_b2/weights/best.pt data=multiclass_small.yaml imgsz=1024 batch=2 epochs=15 optimizer=AdamW lr0=0.0001 lrf=0.1 cos_lr=True mosaic=0 patience=5 workers=0 name=yolo11m_multiclass_finetune_adamw_cos_e15_i1024_b2 project=runs/detect/training
```

`workers=0` was used for stable Windows data loading. It may be increased on a
system where multiprocessing is stable.

## Evaluate on Real Images

The `test` split in each root YAML points to `test_real_new`. These commands place
the evaluation output under `runs/detect/test/`:

```powershell
yolo detect val model=runs/detect/training/yolo11s_final_img1280_sgd_e30_b8/weights/best.pt data=binary_full.yaml imgsz=1280 split=test project=runs/detect/test name=yolo11s_final_img1280_sgd_e30_b8_test_real_new
```

```powershell
yolo detect val model=runs/detect/training/yolo11m_final_img1280_sgd_e30_b4/weights/best.pt data=binary_full.yaml imgsz=1280 split=test project=runs/detect/test name=yolo11m_final_img1280_sgd_e30_b4_test_real_new
```

```powershell
yolo detect val model=runs/detect/training/yolo11m_multiclass_e30_i1024_b2/weights/best.pt data=multiclass_small.yaml imgsz=1024 split=test project=runs/detect/test name=yolo11m_multiclass_e30_i1024_b2_test_real_new
```

To evaluate the fine-tuned multiclass model, replace the model path and run name
with the corresponding fine-tuning directory.

## Prediction

Run prediction on an image directory or video with a trained checkpoint:

```powershell
yolo detect predict model=runs/detect/training/yolo11s_final_img1280_sgd_e30_b8/weights/best.pt source=path/to/images_or_video imgsz=1280 project=runs/detect/predict name=binary_demo
```

## Key Results

### Binary Detection

| Model | Split | Precision | Recall | mAP50 | mAP50-95 | Inference |
|---|---|---:|---:|---:|---:|---:|
| YOLO11s, 1280, 30 epochs | synthetic validation | 97.2% | 95.1% | 97.9% | 90.6% | - |
| YOLO11m, 1280, 30 epochs | synthetic validation | 97.4% | 96.2% | 98.3% | 92.3% | - |
| YOLO11s, 1280, 30 epochs | `test_real_new` | 78.1% | 77.2% | 80.6% | 56.2% | 9.6 ms/image |
| YOLO11m, 1280, 30 epochs | `test_real_new` | 83.5% | 70.4% | 77.8% | 53.2% | 21.4 ms/image |

YOLO11m is the validation-selected model. YOLO11s is the stronger practical
candidate on the independent real-image test split and is also substantially
faster. The broader real-test sweep is recorded in
[`runs/detect/test/yolo11_test_real_new_summary.csv`](runs/detect/test/yolo11_test_real_new_summary.csv).

### Multiclass Detection

| Model | Split | Precision | Recall | mAP50 | mAP50-95 |
|---|---|---:|---:|---:|---:|
| YOLO11m baseline | synthetic validation | 95.3% | 93.0% | 96.1% | 81.4% |
| YOLO11m baseline | `test_real_new` | 66.5% | 77.6% | 73.7% | 55.4% |
| YOLO11m fine-tuned | synthetic validation | 96.7% | 94.4% | 96.8% | 82.6% |
| YOLO11m fine-tuned | `test_real_new` | 72.6% | 72.1% | 72.6% | 55.7% |

The gap between synthetic validation and real testing is the main limitation in
both tasks. Fine-tuning improves synthetic validation but does not improve real
mAP50.

## Experiment Documentation

- [All reports](reports/README.md)
- [Binary model and optimizer screening](reports/experiments/yolo11_binary_optimization.md)
- [Resolution and training strategy](reports/experiments/yolo11_resolution_and_training_strategy.md)
- [Final binary experiments](reports/experiments/yolo11_final_experiment_summary.md)
- [Real-test diagnostic exploration](reports/experiments/yolo11_real_test_extra_exploration.md)
- [Multiclass training summary](reports/experiments/yolo11_multiclass_training_summary.md)
- [Multiclass fine-tuning analysis](reports/experiments/yolo11_multiclass_finetuning_analysis.md)
- [Multiclass real-test analysis](reports/experiments/yolo11_multiclass_real_test_analysis.md)
- [Final report](<reports/pdf/Vision-based Dirt Detection for Cleaning Robot.pdf>)
- [Final presentation](reports/presentations/LabSR+BV_Final_2026_p2_Tao_Song_Ren.pdf)

## Utilities and validation

See [scripts/README.md](scripts/README.md) for utility behavior and safe help
commands. Original tools/*.py commands and the root data-converter command remain
available through compatibility launchers, without duplicate implementations.

```powershell
python -B -m unittest discover -s experiment-analysis/tests -p test_inventory_experiments.py -v
python -B -m unittest discover -s scripts/tests -p test_compatibility.py -v
python -B experiment-analysis/tools/inventory_experiments.py
```

These checks do not train, convert datasets or regenerate reports. Nothing is
automatically staged or pushed. Before a future commit, include moved experimental
evidence together with old-path removals. Run ignore rules now allow lightweight
CSV/YAML/PNG/MP4 records while excluding weights and JPEG preview batches.

## Limitations

- Most training and validation images are synthetic or blended, while the final
  test split contains real images.
- `test_real_new` contains only 80 images, so its estimates have relatively high
  uncertainty.
- The real test data do not include a dedicated background-only subset.
- The real test split was later reused for diagnostic analysis after the original
  validation-selected model generalized poorly. Those later comparisons should
  not be interpreted as a clean hyperparameter-selection benchmark.

## Reference

This project is based on *DirtNet: Visual Dirt Detection for Autonomous Cleaning
Robots* (ICRA 2020) and uses the Ultralytics YOLO11 implementation.
