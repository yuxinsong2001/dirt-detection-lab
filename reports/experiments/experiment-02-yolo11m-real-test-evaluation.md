# 实验报告02：YOLO11M 真实测试集评估

> 测试日期：2026-06-30  
> 报告日期：2026-07-01  
> 模型：实验01的 `best.pt`  
> 测试集：`test_real_new`，80张真实图像

## 1. 评估目的

在不参与训练和模型选择的真实图像上，检验合成数据训练得到的YOLO11M对真实地面污渍及办公室物体的泛化能力，并量化合成到真实的域差距。

## 2. 评估设置

| 项目 | 设置 |
|---|---|
| 权重 | 实验01第29轮 `best.pt` |
| 数据配置 | `cfg/dirt_multiclass_test_real_new.yaml` |
| split | test |
| 图像数 | 80 |
| 实例数 | 644 |
| 纯背景图 | 0 |
| imgsz | 1024 |
| batch | 1 |
| device | CUDA:0 |

评估命令：

```powershell
.\.venv\Scripts\yolo.exe detect val model="D:\DirtNet_Project\runs\detect\runs\yolo11\dirt_multiclass_m_e30_i1024_b2\weights\best.pt" data="D:\DirtNet_Project\cfg\dirt_multiclass_test_real_new.yaml" split=test imgsz=1024 batch=1 device=0 workers=0 plots=True project="D:\DirtNet_Project\runs\yolo11" name=dirt_multiclass_m_best_test_real
```

## 3. 总体结果

| Precision | Recall | mAP50 | mAP50-95 |
|---:|---:|---:|---:|
| 0.665 | 0.776 | 0.737 | 0.554 |

最佳整体F1约为0.70，对应置信度约0.294。默认部署阈值可从0.25到0.30附近开始验证，但最终阈值应由实际业务对漏检和误检的成本决定。

## 4. 逐类别结果

| 类别 | Images | Instances | Precision | Recall | mAP50 | mAP50-95 |
|---|---:|---:|---:|---:|---:|---:|
| dirt | 80 | 360 | 0.852 | 0.706 | 0.773 | 0.489 |
| business_cards | 34 | 41 | 0.892 | 0.756 | 0.852 | 0.685 |
| keys | 23 | 23 | 0.466 | 0.783 | 0.639 | 0.461 |
| other | 19 | 19 | 0.276 | 0.632 | 0.404 | 0.283 |
| paper_and_notebooks | 49 | 61 | 0.802 | 0.869 | 0.878 | 0.695 |
| pens | 34 | 39 | 0.934 | 0.974 | 0.986 | 0.797 |
| rulers | 23 | 23 | 0.539 | 0.508 | 0.490 | 0.353 |
| scissors | 26 | 26 | 0.677 | 0.923 | 0.922 | 0.816 |
| tapes | 24 | 24 | 0.723 | 1.000 | 0.903 | 0.599 |
| usb_sticks | 28 | 28 | 0.485 | 0.607 | 0.520 | 0.360 |

表现最稳定的是 `pens`、`scissors`、`paper_and_notebooks` 和 `business_cards`。最弱的是 `other`、`rulers` 和 `usb_sticks`。`keys`召回率较高但精确率低，表示能找到多数钥匙，同时产生较多错误钥匙预测。

## 5. 合成验证与真实测试对比

| 指标 | 合成验证 | 真实测试 | 绝对下降 |
|---|---:|---:|---:|
| Precision | 0.953 | 0.665 | 0.288 |
| Recall | 0.930 | 0.776 | 0.154 |
| mAP50 | 0.961 | 0.737 | 0.224 |
| mAP50-95 | 0.814 | 0.554 | 0.260 |

Precision下降大于Recall，说明真实场景中的误检增长尤其明显。mAP50-95下降0.260，说明真实条件下不仅分类更难，边界框定位质量也明显下降。

逐类别AP50差距：

| 类别 | 合成AP50 | 真实AP50 | 下降 |
|---|---:|---:|---:|
| pens | 0.994 | 0.986 | 0.008 |
| scissors | 0.995 | 0.922 | 0.073 |
| tapes | 0.995 | 0.903 | 0.092 |
| paper_and_notebooks | 0.995 | 0.878 | 0.117 |
| dirt | 0.908 | 0.773 | 0.135 |
| business_cards | 0.995 | 0.852 | 0.143 |
| keys | 0.982 | 0.639 | 0.343 |
| rulers | 0.860 | 0.490 | 0.370 |
| usb_sticks | 0.924 | 0.520 | 0.404 |
| other | 0.961 | 0.404 | 0.557 |

## 6. 混淆与错误分析

在混淆矩阵工作点下，主要现象为：

- `dirt`：360个真实实例中约260个正确匹配，约56个直接漏检；地面反光和纹理还产生48个污渍假阳性。
- `rulers`：23个实例中约13个正确匹配，约10个漏检。细长透明/浅色外观在暗地面上泛化较差。
- `usb_sticks`：28个实例中约13个正确匹配，且常被预测为 `other`。
- `other`：定义宽泛，容易与钥匙、U盘、剪刀及污渍互相混淆。
- `keys`：Recall为0.783但Precision仅0.466，主要问题是其他物体和反光被误判成钥匙。
- `tapes`：所有24个实例均被召回，但Precision为0.723，仍有额外误检。

真实图像包含暗光、强反光、传感器噪声、地面划痕及真实材质差异，而合成数据未充分覆盖这些变化。这是域差距的主要来源。

## 7. 污渍任务专项判断

`dirt`的Recall为0.706，意味着约29%的真实污渍未被正确检出。Precision为0.852，污渍预测总体较可信，但反光仍会造成误检。

`dirt`的mAP50为0.773，而mAP50-95为0.489，差距0.284。严格IoU下性能下降明显，原因包括污渍形状不规则、边界框标注主观，以及真实污渍边缘不清晰。

若机器人目标是“尽量不漏掉污渍”，部署时可考虑较低置信度阈值，但必须用纯背景地面验证误报率。本测试集没有纯背景图，无法充分评估连续巡检时的背景误报。

## 8. 推理性能

| 阶段 | 每图时间 |
|---|---:|
| 预处理 | 1.1 ms |
| 模型推理 | 30.4 ms |
| 后处理 | 1.7 ms |
| 合计 | 约33.2 ms |

仅按模型流水线计约30 FPS，具备实时推理潜力。实际机器人端速度还会受到相机采集、数据传输、可视化和控制逻辑影响。

## 9. 结论与建议

当前模型是有效的第一版真实场景baseline，但尚不适合作为所有类别都同等可靠的最终模型。增加合成训练轮次不是首选改进方向，下一阶段应优先进行真实域适配：

1. 收集独立的真实训练集和真实验证集。
2. 重点补充 `rulers`、`usb_sticks`、`keys` 和 `other`。
3. 加入纯地面、反光、划痕、阴影等困难负样本。
4. 增强低照度、噪声、曝光和反光变化。
5. 重新审查 `other` 的定义，考虑拆分类别或减少歧义。
6. 根据机器人业务分别选择偏Recall或偏Precision的阈值。

这80张测试图不应直接用于训练或继续选择参数。若决定将其转为训练数据，必须重新收集一套从未参与开发的新真实测试集。

## 10. 关键产物

- [真实测试PR曲线](../../runs/yolo11/dirt_multiclass_m_best_test_real/BoxPR_curve.png)
- [F1—置信度曲线](../../runs/yolo11/dirt_multiclass_m_best_test_real/BoxF1_curve.png)
- [归一化混淆矩阵](../../runs/yolo11/dirt_multiclass_m_best_test_real/confusion_matrix_normalized.png)
- [原始计数混淆矩阵](../../runs/yolo11/dirt_multiclass_m_best_test_real/confusion_matrix.png)
- [预测样例0](../../runs/yolo11/dirt_multiclass_m_best_test_real/val_batch0_pred.jpg)
- [预测样例1](../../runs/yolo11/dirt_multiclass_m_best_test_real/val_batch1_pred.jpg)
- [预测样例2](../../runs/yolo11/dirt_multiclass_m_best_test_real/val_batch2_pred.jpg)

