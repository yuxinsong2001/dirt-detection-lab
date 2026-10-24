# 实验报告01：YOLO11M 多类别合成数据训练与验证

> 实验日期：2026-06-30  
> 报告日期：2026-07-01  
> 任务：10类别目标检测  
> 实验性质：正式合成数据baseline

## 1. 实验目的

验证YOLO11M能否在6 GB显存的RTX 3060 Laptop上，以1024输入分辨率完成DirtNet 10类别目标检测训练，并建立后续真实场景评估的可复现基线。

## 2. 数据设置

数据配置：[`cfg/dirt_multiclass_trainval.yaml`](../../cfg/dirt_multiclass_trainval.yaml)

| 划分 | 图像数 | 标注框数 | 用途 |
|---|---:|---:|---|
| train | 860 | 8,626 | 参数学习 |
| val | 296 | 2,962 | 每轮验证和best模型选择 |
| test_real_new | 80 | 644 | 本实验不使用 |

训练标注分布明显不均衡：`dirt`有5,161个实例，而`scissors`仅114个、`rulers`与`tapes`各162个。

## 3. 环境与参数

| 项目 | 设置 |
|---|---|
| GPU | NVIDIA GeForce RTX 3060 Laptop GPU，6 GB |
| Python | 3.12.10 |
| PyTorch | 2.12.1+cu130 |
| Ultralytics | 8.4.74 |
| 模型 | YOLO11M，COCO预训练 |
| 参数量 | 约20.0M（融合后20,037,742） |
| 输入尺寸 | 1024 |
| batch | 2 |
| epochs | 30 |
| optimizer | auto |
| AMP | 开启 |
| workers | 0 |
| seed | 0 |
| deterministic | True |

完整有效参数见[`args.yaml`](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/args.yaml)。本次由于启动时工作目录和相对 `project` 组合，结果保存到了嵌套目录；这不影响模型数值结果。

## 4. 训练结果

训练完整运行30轮，耗时5,045.91秒，约84.1分钟，未发生OOM。综合最佳轮次为第29轮。

| 指标 | 第29轮best | 第30轮last |
|---|---:|---:|
| Precision | 0.9535 | 0.9415 |
| Recall | 0.9305 | 0.9387 |
| mAP50 | 0.9608 | 0.9581 |
| mAP50-95 | 0.8136 | 0.8082 |
| train box loss | 0.6516 | 0.6363 |
| val box loss | 0.7059 | 0.7349 |

第30轮训练损失继续下降，但验证定位损失和mAP略有回落，因此应使用第29轮对应的 `best.pt`。

## 5. 逐类别AP50

| 类别 | AP50 |
|---|---:|
| business_cards | 0.995 |
| paper_and_notebooks | 0.995 |
| scissors | 0.995 |
| tapes | 0.995 |
| pens | 0.994 |
| keys | 0.982 |
| other | 0.961 |
| usb_sticks | 0.924 |
| dirt | 0.908 |
| rulers | 0.860 |

合成验证集中最弱的类别是 `rulers`，其次是 `dirt` 和 `usb_sticks`。尺子样本少且目标细长；污渍外观和尺度变化大，边界定义也更困难。

## 6. 收敛与过拟合判断

[`results.png`](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/results.png)显示：

- 三项训练损失持续下降。
- 验证损失总体下降，后期仅有小幅波动。
- mAP50与mAP50-95一直提升到第29轮。
- 没有出现验证性能长期恶化的明显过拟合。

因此30轮作为baseline是合理的。继续增加合成训练轮次可能获得小幅收益，但不是解决真实场景泛化问题的主要手段。

## 7. 结论

本实验达到预期：YOLO11M能够在6 GB显存上以 `imgsz=1024、batch=2` 稳定训练，合成验证集检测与分类表现优秀。该结果证明数据转换、10类输出层和训练流程均可用。

但合成验证集与训练集共享相近的生成分布，高分不能直接代表真实机器人场景性能。真实泛化能力必须由独立的80张真实测试图评估。

## 8. 关键产物

目录整理说明：原 best.pt 在本机以 best_dirt_multiclass_11m_e30_i1024_b2.pt 保存；已核对其 SHA-256 与本报告记录一致。链接采用现存文件名，未改动权重内容。

- [最佳权重best.pt](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/weights/best_dirt_multiclass_11m_e30_i1024_b2.pt)
- [最后权重last.pt](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/weights/last.pt)
- [逐轮结果results.csv](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/results.csv)
- [训练曲线](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/results.png)
- [PR曲线](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/BoxPR_curve.png)
- [归一化混淆矩阵](../../runs/detect/runs/yolo11/dirt_multiclass_m_e30_i1024_b2/confusion_matrix_normalized.png)

`best.pt` SHA256：`EFC9968722A442C3A6D95D4B6186D62C0A3FE3FDC322439DA2D02D409D153790`

