# 实验数据分析系统 / Experiment Analysis

这是基于原 YOLO 项目新增的独立功能模块：读取已有实验记录，逐步实现数据检查、整理、查询和分析。它不训练新的 YOLO，也不复制原始实验数据。

当前主线：以官方已完成的YOLO训练记录为输入，不使用个人历史训练结果作为前期分析依据。COCO重新评估、LCBench和NAS-Bench暂不执行。先核验官方来源，再导出配置和曲线，之后设计查询与比较。

本次新增的功能代码、测试、生成结果和学习说明，都集中在这里，不再散放到原项目的 tools、tests 或 reports 中。

```text
experiment-analysis/
  README.md                 ← 总入口：本模块是什么、如何使用
  tools/
    inventory_experiments.py← 已实现：实验清点程序
    inspect_official_checkpoint.py ← 已实现：新下载官方文件并提取历史记录
  tests/
    test_inventory_experiments.py
                            ← 已实现：6项自动测试
  reports/
    inventory/              ← 程序生成的 JSON 清单
    official/               ← 官方记录的配置、逐轮指标和来源
  data/external/            ← 官方下载文件，仅本地缓存，不上传
  local-work-notes/          ← 个人讲解，不上传
    README.md               ← 学习说明入口
    steps/                  ← 本次逐步讲解、中德术语、面试追问
    legacy-training/        ← 原先学习资料的历史归档
    maintenance/            ← 目录整理记录，仅需追溯时查看
```

## 当前完成情况

已实现并验证：原实验清点工具（6项测试），以及官方YOLO26n来源核验和记录提取（7项测试）。官方文件提取到113项配置、245行逐轮记录和11项保存指标。

[官方结果说明](reports/official/yolo26n-v8.4.0/README.md)。这是一份官方运行的历史记录，不是大规模参数搜索数据集；尚未做跨模型结论。

尚未开始：多模型统一结构与可比性检查、数据库、模型比较图表、交互页面。

## 从仓库根目录运行

```powershell
cd D:\DirtNet_Project
python experiment-analysis/tools/inventory_experiments.py
python -m unittest discover -s experiment-analysis/tests -p test_inventory_experiments.py -v
python -B -m unittest discover -s experiment-analysis/tests -p "test_*.py" -v
```

默认扫描原项目的 runs，不是本模块内部目录。已有清单保存在 reports/inventory；新增结果时请使用新的文件名，程序拒绝覆盖已有文件：

```powershell
python experiment-analysis/tools/inventory_experiments.py --output experiment-analysis/reports/inventory/inventory-new.json
```

## 什么会上传？

tools、tests 和 reports 作为项目交付内容分批提交到本地 Git，尚未推送。local-work-notes 通过本机 .git/info/exclude 排除；正常 Git 操作不会上传，勿强制添加。Git 忽略不提供备份。

原 YOLO 训练数据和实验结果仍在仓库的 data、datasets、runs 中，程序只读取，不复制到这里。

官方提取工具只接受固定发布版和校验值，不自动选择latest；本次从官方新下载，没有复用根目录个人文件。原清点工具仍可使用，但不会自动进入官方记录分析。新工具的默认输出和下载位置已存在，再次执行会明确拒绝覆盖，不会训练或替换结果。
