# 2026_p02_dirt_detection
Students: Shufang Tao (3824652), Yuxin Song (3820779), Yuyang Ren (3762594)

# 🚀 DirtNet: Visual Dirt Detection Project

This project is implemented based on the **YOLOv3** framework. It focuses on automatic detection and classification of **dirt** and common **office objects** on floors in office environments. The project is inspired by the core architecture of the ICRA 2020 paper *DirtNet: Visual Dirt Detection for Autonomous Cleaning Robots*.

## 📋 Environment

To ensure the experiment is reproducible, please run all commands in **Anaconda Prompt** or **Miniconda Prompt**.

- **Operating System**: Windows 10/11
- **Python**: 3.8.20
- **Deep Learning Framework**:
  - `torch == 2.4.1` with CUDA 13.0 hardware acceleration support
  - `torchvision == 0.19`
- **Main Dependencies**: See `requirements.txt` in this repository.

## 🛠️ Quick Start

### 1. Create and activate the environment

```dos
conda create -n dirtnet python=3.8.20 -y
conda activate dirtnet
pip install -r requirements.txt
```

### 2. ⚠️ Critical Windows Fix

Before running any script in Anaconda Prompt, execute the following command to resolve the OpenMP library conflict. Otherwise, the program may exit immediately.

```dos
set KMP_DUPLICATE_LIB_OK=TRUE
```

### 3. Dataset Setup

Please make sure the dataset is stored in the following structure so that `dirt.yaml` can resolve the paths correctly:

```text
D:\DIRTNET_PROJECT\
├── data\               <-- Contains images/ and labels/ subfolders
└── yolov3-master\      <-- Contains training code and configuration files
```

## 🏋️ Training

This experiment uses a **1024x832** rectangular training strategy, which improves accuracy while reducing computational cost by about **19%** in FLOPs.

```dos
python train.py --img 1024 --batch 2 --epochs 15 --data dirt.yaml --weights yolov3.pt
```

*Note: The model is trained for 15 epochs. The best weights are usually produced between epoch 10 and epoch 15.*

## 📊 Latest Results

According to the latest training record (`exp3`), the model achieved the following performance on the validation set:

| Class | Images | Precision (P) | Recall (R) | mAP@0.5 |
| :--- | :--- | :--- | :--- | :--- |
| **Overall** | 296 | 0.929 | 0.909 | **93.6%** |
| **Dirt** | 296 | 0.908 | 0.855 | 89.5% |
| **Object** | 296 | 0.949 | 0.963 | 97.6% |

- **Best weight file**: `runs/train/exp3/weights/best.pt`
- **Total training time**: about 0.6 hours

## 📁 Directory Structure

```text
DIRTNET_PROJECT/
├── data/               # Dataset (images and labels)
│   ├── images/         # Includes train (860+), val (296), test_real (80)
│   └── labels/         # Corresponding .txt annotation files
└── yolov3-master/      # Main code directory
    ├── dirt.yaml       # Configuration file; verify path references before training
    └── runs/train/exp3 # Training outputs, including PR curves, confusion matrices, and weights
```

## 🤝 Collaboration Notes

1. **Real-world data validation**: Run the following command to test `best.pt` on the 80 real-world photos in `test_real_new`:
   ```dos
   python detect.py --weights runs/train/exp3/weights/best.pt --img 1024 --source ../data/images/test_real_new
   ```
2. **Reading model weights**: `best.pt` is a binary file and cannot be previewed directly. It must be loaded through code.
3. **Avoid Git bloat**: `.gitignore` is configured to ignore the `data/` directory and large weight files. Do not manually add large dataset files or model weights.
4. **GPU memory optimization**: If you encounter `CUDA out of memory`, try changing `--batch 2` to `--batch 1`.

---

*This project is developed based on the Ultralytics YOLOv3 community version.*

---

# 中文版本

# 🚀 DirtNet: Visual Dirt Detection Project

本项目基于 **YOLOv3** 框架实现，专注于办公环境地面上的 **污垢 (Dirt)** 与 **典型办公物体 (Object)** 的自动识别与分类。本项目参考了 ICRA 2020 论文 《DirtNet: Visual Dirt Detection for Autonomous Cleaning Robots》 的核心架构。

## 📋 环境要求 (Environment)
为确保实验可复现，请务必使用 **Anaconda Prompt** 或 **Miniconda Prompt** 运行。

- **操作系统**: Windows 10/11
- **Python**: 3.8.20
- **深度学习框架**: 
  - `torch == 2.4.1` (支持 CUDA 13.0 硬件加速)
  - `torchvision == 0.19`
- **主要依赖**: 请参考仓库中的 `requirements.txt`。

## 🛠️ 快速上手 (Quick Start)

### 1. 创建并激活环境
```dos
conda create -n dirtnet python=3.8.20 -y
conda activate dirtnet
pip install -r requirements.txt
```

### 2. ⚠️ Windows 运行必读 (Critical Fix)
在 Anaconda Prompt 中运行任何脚本前，必须执行以下命令解决 OpenMP 库冲突，否则程序将直接退出：

```dos
set KMP_DUPLICATE_LIB_OK=TRUE
```

### 3. 数据集准备 (Dataset Setup)
请确保数据集存放路径如下，以便 `dirt.yaml` 自动解析：

```text
D:\DIRTNET_PROJECT\
├── data\               <-- 包含 images/ 和 labels/ 子文件夹
└── yolov3-master\      <-- 存放训练代码与配置文件
```

## 🏋️ 训练指令 (Training)
本实验采用 **1024x832** 矩形训练方案，在提升精度的同时可节省 **19%** 的计算量 (FLOPs)：

```dos
python train.py --img 1024 --batch 2 --epochs 15 --data dirt.yaml --weights yolov3.pt
```
*注：训练层级需要 15 轮，最佳权重通常在第 10 到 15 轮 (Epoch) 之间产生。*

## 📊 实验成果总结 (Latest Results)
根据最近一次训练记录（exp3），模型在验证集上表现如下：

| 类别 (Class) | 图像数 (Images) | 精准率 (P) | 召回率 (R) | mAP@0.5 |
| :--- | :--- | :--- | :--- | :--- |
| **整体 (Overall)** | 296 | 0.929 | 0.909 | **93.6%** |
| **Dirt (污垢)** | 296 | 0.908 | 0.855 | 89.5% |
| **Object (物体)** | 296 | 0.949 | 0.963 | 97.6% |

- **最佳权重存储**: `runs/train/exp3/weights/best.pt`
- **训练总时长**: 约 0.6 小时

## 📁 目录结构参考
```text
DIRTNET_PROJECT/
├── data/               # 数据集 (Images & Labels)
│   ├── images/         # 包含 train (860+), val (296), test_real (80)
│   └── labels/         # 对应图片的 .txt 标注文件
└── yolov3-master/      # 代码主目录
    ├── dirt.yaml       # 配置文件 (需确认路径引用正确)
    └── runs/train/exp3 # 训练产物 (PR曲线、混淆矩阵、权重文件)
```

## 🤝 队友协作注意事项
1. **真实数据验证**: 请运行以下命令，使用 `best.pt` 测试 `test_real_new` 中的 80 张真实照片：
   ```dos
   python detect.py --weights runs/train/exp3/weights/best.pt --img 1024 --source ../data/images/test_real_new
   ```
2. **读取权重**: `best.pt` 为二进制文件，无法直接打开预览，需通过代码加载。
3. **防止 Git 冗余**: `.gitignore` 已配置忽略 `data/` 目录及大型权重文件，请勿手动 `git add` 大容量数据。
4. **显存优化**: 若运行报错 `CUDA out of memory`，请尝试将 `--batch 2` 调整为 `1`。

---
*本项目代码基于 Ultralytics YOLOv3 社区版二次开发。*
