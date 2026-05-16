# 2026_p02_dirt_detection

Students: Shufang Tao (3824652), Yuxin Song (3820779), Yuyang Ren (3762594)

Language: [中文](#中文) | [English](#english)

---

## 中文

# 🚀 DirtNet: Visual Dirt Detection Project

本项目基于 **YOLOv3** 框架实现，专注于办公环境地面上的 **污垢 (Dirt)** 与 **典型办公物体 (Object)** 的自动识别与分类。本项目参考了 ICRA 2020 论文 《DirtNet: Visual Dirt Detection for Autonomous Cleaning Robots》 的核心架构。

## 📋 环境要求 (Environment)

为确保实验可复现，建议使用 **Anaconda Prompt** 或 **Miniconda Prompt** 运行。

本项目已在以下 Windows 环境中成功运行：

| 操作系统 | Python | PyTorch / CUDA |
|---|---|---|
| Windows | 3.8.20 | torch 2.4.1 / CUDA 13.0 |
| Windows | 3.12.13 | torch 2.12.0 / CUDA 13.2 |

主要依赖请参考仓库中的 `requirements.txt`。不同机器的 CUDA 和 PyTorch 版本可能略有差异，实际以能完成训练、验证和测试流程为准。

## 🛠️ 快速上手 (Quick Start)

### 1. 创建并激活环境

可选择一个已验证的 Python 版本创建环境：

```dos
conda create -n dirtnet python=3.12 -y
conda activate dirtnet
pip install -r requirements.txt
```

### 2. Windows 可选修复 (Optional Fix)

如果运行时出现 OpenMP / MKL duplicate library 相关报错，可执行：

```dos
set KMP_DUPLICATE_LIB_OK=TRUE
```

### 3. 数据集准备 (Dataset Setup)

请确保数据集包含 `images/` 和 `labels/` 两部分，并与 `dirt.yaml` 中的路径保持一致：

```text
DIRTNET_PROJECT/
├── data/
│   ├── images/         <-- 存放训练、验证和测试图片
│   └── labels/         <-- 存放对应的 YOLO 格式标注文件
└── yolov3-master/      <-- 存放训练代码与配置文件
```

## 🏋️ 训练指令 (Training)

本实验采用 **1024x832** 矩形训练方案：

```dos
python train.py --img 1024 --batch 2 --epochs 15 --data dirt.yaml --weights yolov3.pt
```

主要参数说明：

| 参数 | 含义 | 当前设置 |
| :--- | :--- | :--- |
| `--img` | 输入图像尺寸 | `1024` |
| `--batch` | 每次训练输入的图片数量 | `2` |
| `--epochs` | 训练轮数 | `15` |
| `--data` | 数据集配置文件 | `dirt.yaml` |
| `--weights` | 初始权重文件 | `yolov3.pt` |

*注：根据原论文，该训练方案在提升精度的同时可节省约 **19%** 的计算量 (FLOPs)；训练 15 轮后通常可得到最佳权重。*

## 📊 实验成果总结 (Latest Results)

根据最近一次训练记录（exp3），模型在验证集上表现如下：

| 类别 (Class) | 图像数 (Images) | 精准率 (P) | 召回率 (R) | mAP@0.5 |
| :--- | :--- | :--- | :--- | :--- |
| **整体 (Overall)** | 296 | 0.929 | 0.909 | **93.6%** |
| **Dirt (污垢)** | 296 | 0.908 | 0.855 | 89.5% |
| **Object (物体)** | 296 | 0.949 | 0.963 | 97.6% |

- **最佳权重存储**: `runs/train/exp3/weights/best.pt`
- **训练总时长**: 约 0.6 小时

## 📐 Evaluation Metrics

本项目主要使用以下指标评估检测效果：

| 指标 | 含义 |
| :--- | :--- |
| Precision | 预测为目标的框中，有多少是真正正确的 |
| Recall | 真实目标中，有多少被模型成功检测到 |
| F1 | Precision 和 Recall 的综合指标 |
| mAP@0.5 | IoU 阈值为 0.5 时的平均检测精度 |

除定量指标外，也会结合成功检测、漏检、误检和类别混淆案例进行定性分析。

## 📁 目录结构参考

```text
DIRTNET_PROJECT/
├── data/               # 数据集 (Images & Labels)
│   ├── images/         # 包含 train (860+), val (296), test_real (80)
│   └── labels/         # 对应图片的 YOLO 格式 .txt 标注文件
└── yolov3-master/      # 代码主目录
    ├── dirt.yaml       # 数据集配置文件
    └── runs/train/     # 训练产物 (PR曲线、混淆矩阵、权重文件)
```

## 🤝 队友协作注意事项

1. **真实数据验证**: 请运行以下命令，使用 `best.pt` 测试 `test_real_new` 中的真实照片：
   ```dos
   python detect.py --weights runs/train/dirt_binary_train/weights/best.pt --img 1024 --source ../data/images/test_real_new
   ```
2. **定量评估**: 如需在验证集或测试集上计算指标，请使用 `val.py`，并记录 precision、recall、mAP@0.5 和 F1 等结果。
3. **读取权重**: `best.pt` 为二进制文件，无法直接打开预览，需通过代码加载。
4. **防止 Git 冗余**: `.gitignore` 已配置忽略 `data/` 目录及大型权重文件，请勿手动 `git add` 大容量数据。
5. **显存优化**: 若运行报错 `CUDA out of memory`，请尝试将 `--batch 2` 调整为 `1`。

---

## English

# DirtNet: Visual Dirt Detection Project

This project is a YOLOv3-based reproduction of the ICRA 2020 paper **DirtNet: Visual Dirt Detection for Autonomous Cleaning Robots**. It focuses on detecting **dirt** and typical office **objects** on the floor.

## Environment

To make the experiments reproducible, using **Anaconda Prompt** or **Miniconda Prompt** is recommended.

The project has been successfully run on the following Windows environments:

| OS | Python | PyTorch / CUDA |
|---|---|---|
| Windows | 3.8.20 | torch 2.4.1 / CUDA 13.0 |
| Windows | 3.12.13 | torch 2.12.0 / CUDA 13.2 |

Main dependencies are listed in `requirements.txt`. CUDA and PyTorch versions may vary across machines, as long as training, validation, and testing can run successfully.

## Quick Start

### 1. Create and Activate Environment

Create an environment with one verified Python version:

```dos
conda create -n dirtnet python=3.12 -y
conda activate dirtnet
pip install -r requirements.txt
```

### 2. Optional Windows Fix

If an OpenMP / MKL duplicate library error occurs, run:

```dos
set KMP_DUPLICATE_LIB_OK=TRUE
```

### 3. Dataset Setup

Make sure the dataset contains both `images/` and `labels/`, and that their paths match `dirt.yaml`:

```text
DIRTNET_PROJECT/
├── data/
│   ├── images/         <-- training, validation, and test images
│   └── labels/         <-- corresponding YOLO-format annotation files
└── yolov3-master/      <-- training code and configuration files
```

## Training

This experiment uses a **1024x832** rectangular training setup:

```dos
python train.py --img 1024 --batch 2 --epochs 15 --data dirt.yaml --weights yolov3.pt
```

Main parameters:

| Parameter | Meaning | Current setting |
| :--- | :--- | :--- |
| `--img` | Input image size | `1024` |
| `--batch` | Number of images per training batch | `2` |
| `--epochs` | Number of training epochs | `15` |
| `--data` | Dataset configuration file | `dirt.yaml` |
| `--weights` | Initial weight file | `yolov3.pt` |

*Note: According to the original paper, this training setup can improve accuracy while saving about **19%** FLOPs. The best weights are usually obtained after 15 epochs.*

## Latest Results

According to the latest training record (`exp3`), the model performs as follows on the validation set:

| Class | Images | Precision (P) | Recall (R) | mAP@0.5 |
| :--- | :--- | :--- | :--- | :--- |
| **Overall** | 296 | 0.929 | 0.909 | **93.6%** |
| **Dirt** | 296 | 0.908 | 0.855 | 89.5% |
| **Object** | 296 | 0.949 | 0.963 | 97.6% |

- **Best weights**: `runs/train/exp3/weights/best.pt`
- **Training time**: about 0.6 hours

## Evaluation Metrics

This project mainly uses the following metrics:

| Metric | Meaning |
| :--- | :--- |
| Precision | How many predicted boxes are correct |
| Recall | How many ground-truth targets are detected |
| F1 | Combined score of precision and recall |
| mAP@0.5 | Mean average precision at IoU threshold 0.5 |

In addition to quantitative metrics, qualitative analysis includes successful detections, missed detections, false positives, and class confusion cases.

## Repository Structure

```text
DIRTNET_PROJECT/
├── data/               # Dataset (Images & Labels)
│   ├── images/         # includes train (860+), val (296), test_real (80)
│   └── labels/         # corresponding YOLO-format .txt annotation files
└── yolov3-master/      # code directory
    ├── dirt.yaml       # dataset configuration file
    └── runs/train/     # training outputs (curves, confusion matrix, weights)
```

## Collaboration Notes

1. **Real data testing**: run the following command to test `best.pt` on images from `test_real_new`:
   ```dos
   python detect.py --weights runs/train/dirt_binary_train/weights/best.pt --img 1024 --source ../data/images/test_real_new
   ```
2. **Quantitative evaluation**: use `val.py` to evaluate validation or test sets, and record precision, recall, mAP@0.5, and F1.
3. **Weights**: `best.pt` is a binary weight file and should be loaded through code.
4. **Git hygiene**: `data/`, large weight files, and generated experiment outputs should not be committed.
5. **Memory optimization**: if `CUDA out of memory` occurs, try changing `--batch 2` to `--batch 1`.

---

*This project is based on the Ultralytics YOLOv3 community implementation.*
