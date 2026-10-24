# YOLO11M 多类别目标检测正式训练操作手册

> 项目：DirtNet 多类别地面物体检测  
> 平台：Windows、RTX 3060 Laptop 6 GB  
> 基线：YOLO11M、`imgsz=1024`、`batch=2`、30 epochs  
> 更新日期：2026-07-01

## 1. 目的与边界

本文用于从一个新的 PowerShell 会话开始，完成环境检查、显存准备、正式训练、断点续训、合成验证和真实测试。正式基线只更换模型、数据集与运行名称，其余主要设置继承此前 YOLO11L 实验。

固定原则：

- 模型固定为 `yolo11m.pt`。
- 首次训练固定使用 `imgsz=1024`、`batch=2`、30 epochs。
- 仅在出现 `CUDA out of memory` 时先把 `batch` 降为1；仍失败才降低 `imgsz`。
- 真实测试集不参与训练、早停、阈值选择或超参数选择。
- 正式使用 `best.pt`，不默认使用最后一轮的 `last.pt`。

## 2. 关键路径

| 用途 | 路径 |
|---|---|
| 项目根目录 | `D:\DirtNet_Project` |
| Python虚拟环境 | `.venv` |
| 本地Ultralytics源码 | `ultralytics-repo` |
| 预训练权重 | `yolo11m.pt` |
| 训练/验证配置 | `cfg/dirt_multiclass_trainval.yaml` |
| 真实测试配置 | `cfg/dirt_multiclass_test_real_new.yaml` |
| 标准输出根目录 | `D:\DirtNet_Project\runs\yolo11` |

数据集包含10类：`dirt`、`business_cards`、`keys`、`other`、`paper_and_notebooks`、`pens`、`rulers`、`scissors`、`tapes`、`usb_sticks`。

## 3. 训练前准备

### 3.1 释放显存

正常关闭浏览器、视频软件、动态壁纸、游戏、NVIDIA Overlay和其他Python训练进程。不要强制结束Windows桌面、驱动或不明系统进程。

检查GPU：

```powershell
nvidia-smi
```

判断标准：

- GPU应显示为 `NVIDIA GeForce RTX 3060 Laptop GPU`。
- 不应存在其他深度学习训练进程。
- 瞬时空闲显存不是硬件容量；本机稳定约束始终是6 GB总显存。

### 3.2 进入项目并激活环境

```powershell
Set-Location D:\DirtNet_Project
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
$env:YOLO_CONFIG_DIR="$PWD\.ultralytics"
$env:PYTHONPATH="$PWD\ultralytics-repo"
```

激活成功后，提示符前应出现 `(.venv)`。

### 3.3 验证Python、PyTorch与CUDA

```powershell
python -c "import sys, torch, ultralytics; print('Python:', sys.version); print('Executable:', sys.executable); print('PyTorch:', torch.__version__); print('Ultralytics:', ultralytics.__version__); print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

本次已验证的环境为：

- Python 3.12.10
- PyTorch 2.12.1+cu130
- Ultralytics 8.4.74
- CUDA可用
- RTX 3060 Laptop GPU 6 GB

若 `sys.executable` 不是 `D:\DirtNet_Project\.venv\Scripts\python.exe`，不要开始训练。

### 3.4 验证模型和数据配置

```powershell
Test-Path .\yolo11m.pt
Test-Path .\cfg\dirt_multiclass_trainval.yaml
Test-Path .\data\multiclass\images\train
Test-Path .\data\multiclass\labels\train
```

四项都应返回 `True`。当前数据规模为：训练860张、验证296张、真实测试80张。

## 4. 启动正式训练

从项目根目录执行下面一整行命令：

```powershell
.\.venv\Scripts\yolo.exe detect train model="D:\DirtNet_Project\yolo11m.pt" data="D:\DirtNet_Project\cfg\dirt_multiclass_trainval.yaml" epochs=30 patience=100 batch=2 imgsz=1024 device=0 workers=0 project="D:\DirtNet_Project\runs\yolo11" name=dirt_multiclass_m_e30_i1024_b2 exist_ok=False pretrained=True optimizer=auto seed=0 deterministic=True amp=True cache=False single_cls=False rect=False cos_lr=False close_mosaic=10 save=True save_period=-1 val=True plots=True
```

使用绝对 `project` 路径可以避免在错误工作目录下生成 `runs/detect/runs/yolo11` 这样的嵌套目录。

### 4.1 参数说明

| 参数 | 值 | 目的 |
|---|---:|---|
| `epochs` | 30 | 控制正式基线训练长度 |
| `batch` | 2 | 6 GB显存上的首选起点 |
| `imgsz` | 1024 | 保留小污渍和细长物体细节 |
| `workers` | 0 | 避免Windows多进程读取问题 |
| `optimizer` | auto | 继承旧基线策略 |
| `amp` | True | 使用混合精度降低显存需求 |
| `seed` | 0 | 固定随机种子 |
| `deterministic` | True | 提高可复现性 |
| `single_cls` | False | 明确执行10类别检测 |
| `close_mosaic` | 10 | 最后10轮关闭Mosaic以稳定收敛 |
| `cache` | False | 避免额外内存压力 |
| `save_period` | -1 | 保存标准的best/last权重 |

### 4.2 正常启动标志

以下内容是正常现象：

```text
Overriding model.yaml nc=80 with nc=10
```

它表示将COCO预训练模型的80类检测头替换为当前10类检测头。随后应看到860张训练图、296张验证图、`Epoch 1/30`和GPU显存占用。

## 5. 训练中监控

在另一个PowerShell窗口执行：

```powershell
nvidia-smi -l 2
```

显存接近6 GB、GPU利用率较高并不等于故障。真正需要处理的是：

```text
CUDA out of memory
```

每轮关注：

- `train/box_loss`、`train/cls_loss`、`train/dfl_loss`总体下降。
- 验证损失不要持续恶化。
- `mAP50`与`mAP50-95`总体上升。
- 单轮波动正常，应看连续趋势。

## 6. OOM降级顺序

### 6.1 第一次OOM：只降低batch

```powershell
.\.venv\Scripts\yolo.exe detect train model="D:\DirtNet_Project\yolo11m.pt" data="D:\DirtNet_Project\cfg\dirt_multiclass_trainval.yaml" epochs=30 patience=100 batch=1 imgsz=1024 device=0 workers=0 project="D:\DirtNet_Project\runs\yolo11" name=dirt_multiclass_m_e30_i1024_b1 exist_ok=False pretrained=True optimizer=auto seed=0 deterministic=True amp=True cache=False single_cls=False rect=False cos_lr=False close_mosaic=10 save=True save_period=-1 val=True plots=True
```

### 6.2 `batch=1`仍OOM：再降低分辨率

先尝试 `imgsz=832`，运行名称改为 `dirt_multiclass_m_e30_i832_b1`。仍失败时最后使用 `imgsz=640`。不要在一次实验中同时随意修改学习率、增强和模型规模，否则失去可比性。

## 7. 中断与恢复

至少完成一轮后，可从 `last.pt` 恢复：

```powershell
.\.venv\Scripts\yolo.exe detect train model="D:\DirtNet_Project\runs\yolo11\dirt_multiclass_m_e30_i1024_b2\weights\last.pt" resume=True
```

恢复时不要重新指定一套训练参数；检查点会恢复epoch、优化器和学习率状态。若第一轮尚未完成，通常没有可用的完整恢复点，应重新启动正式命令。

## 8. 训练后验证

### 8.1 合成验证集

```powershell
.\.venv\Scripts\yolo.exe detect val model="D:\DirtNet_Project\runs\yolo11\dirt_multiclass_m_e30_i1024_b2\weights\best.pt" data="D:\DirtNet_Project\cfg\dirt_multiclass_trainval.yaml" split=val imgsz=1024 batch=1 device=0 workers=0 plots=True project="D:\DirtNet_Project\runs\yolo11" name=dirt_multiclass_m_best_val
```

### 8.2 真实测试集

模型和参数冻结后，仅执行最终测试：

```powershell
.\.venv\Scripts\yolo.exe detect val model="D:\DirtNet_Project\runs\yolo11\dirt_multiclass_m_e30_i1024_b2\weights\best.pt" data="D:\DirtNet_Project\cfg\dirt_multiclass_test_real_new.yaml" split=test imgsz=1024 batch=1 device=0 workers=0 plots=True project="D:\DirtNet_Project\runs\yolo11" name=dirt_multiclass_m_best_test_real
```

若训练结果实际位于旧的嵌套目录，应把 `model` 改为：

```text
D:\DirtNet_Project\runs\detect\runs\yolo11\dirt_multiclass_m_e30_i1024_b2\weights\best.pt
```

## 9. 输出文件说明

| 文件 | 用途 |
|---|---|
| `weights/best.pt` | 验证综合指标最佳的正式模型 |
| `weights/last.pt` | 最后一轮模型，主要用于恢复 |
| `args.yaml` | 完整有效参数，是复现实验的关键 |
| `results.csv` | 每轮损失与指标 |
| `results.png` | 收敛曲线 |
| `BoxPR_curve.png` | 各类别PR曲线和AP50 |
| `confusion_matrix_normalized.png` | 各类别混淆、漏检和误检 |
| `val_batch*_pred.jpg` | 定性检查预测结果 |

## 10. 可复现记录清单

每次正式实验至少记录：

- 模型文件名与SHA256。
- Ultralytics、PyTorch、CUDA版本。
- 数据YAML及类别顺序。
- train/val/test图像数和实例数。
- 完整命令和 `args.yaml`。
- GPU型号、batch、imgsz和训练时间。
- best epoch、Precision、Recall、mAP50、mAP50-95。
- 逐类别指标和混淆矩阵。
- 是否发生OOM、恢复或人工中断。

另可配合仓库中的[可复现训练检查表](../reference/yolo11-reproducible-training-checklist.html)使用。

