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
    compare_official_configs.py ← 已实现：N/S配置逐字段对照，不排名
    build_performance_summary.py ← 已实现：整理官方发布性能和资源取舍
  tests/
    test_inventory_experiments.py
                            ← 已实现：6项自动测试
  reports/
    inventory/              ← 程序生成的 JSON 清单
    official/               ← 官方记录的配置、逐轮指标和来源
  data/external/            ← 官方下载文件，仅本地缓存，不上传
  data/reference/           ← 带日期与来源的官方性能表转录
  local-work-notes/          ← 个人讲解，不上传
    README.md               ← 学习说明入口
    steps/                  ← 本次逐步讲解、中德术语、面试追问
    legacy-training/        ← 原先学习资料的历史归档
    maintenance/            ← 目录整理记录，仅需追溯时查看
```

## 当前完成情况

已实现：原实验清点、官方N/S来源核验与记录提取、配置对照。N有245轮，S有70轮；两者各113项配置、11项保存指标。113项配置中77项保存值相同、36项不同。

[官方结果说明](reports/official/yolo26n-v8.4.0/README.md)。这是一份官方运行的历史记录，不是大规模参数搜索数据集。

[第二个官方模型YOLO26s](reports/official/yolo26s-v8.4.0/README.md) · [N/S配置对照](reports/official/comparison-n-s-v8.4.0/README.md)。配置对照是描述性检查，不证明单个参数的因果作用。

[N/S性能比较与总表](reports/official/performance-n-s-2026-10-24/README.md)：比较各自官方优化后的发布方案，允许训练参数不同。普通检测、端到端检测和旧checkpoint保存指标分别保留；官方测速细节不完整的部分标为未知。已完成文档口径检查，未独立运行评估。

尚未开始：独立复现评估、数据库、性能图表和交互页面。

## 从仓库根目录运行

```powershell
cd D:\DirtNet_Project
python experiment-analysis/tools/inventory_experiments.py
python -m unittest discover -s experiment-analysis/tests -p test_inventory_experiments.py -v
python -B -m unittest discover -s experiment-analysis/tests -p "test_*.py" -v
python experiment-analysis/tools/build_performance_summary.py
```

默认扫描原项目的 runs，不是本模块内部目录。已有清单保存在 reports/inventory；新增结果时请使用新的文件名，程序拒绝覆盖已有文件：

```powershell
python experiment-analysis/tools/inventory_experiments.py --output experiment-analysis/reports/inventory/inventory-new.json
```

## 什么会上传？

tools、tests 和 reports 是可纳入 Git 的项目交付内容；提交和推送按用户指示进行。local-work-notes 通过本机 .git/info/exclude 排除；正常 Git 操作不会上传，勿强制添加。Git 忽略不提供备份。

原 YOLO 训练数据和实验结果仍在仓库的 data、datasets、runs 中，程序只读取，不复制到这里。

官方提取工具只接受固定发布版和校验值，不自动选择latest；本次从官方新下载，没有复用根目录个人文件。原清点工具仍可使用，但不会自动进入官方记录分析。新工具的默认输出和下载位置已存在，再次执行会明确拒绝覆盖，不会训练或替换结果。

提取工具支持 --model yolo26n.pt 或 --model yolo26s.pt。配置对照命令为 python experiment-analysis/tools/compare_official_configs.py；对照输出已存在时同样拒绝覆盖。现有结果无需重复生成。

## Database design preparation (step 1)

`tools/prepare_database_design.py` reads the existing 10 N/S JSON/CSV inputs, inventories fields, checks selected CSV/JSON values and source associations, and maps 34 proposed measurements. It generates `field-inventory.csv`, `mapping-verification.md`, and `storage-design.md`. The design is a manually authored template under `tools/templates/database-design/`; the tool does not infer a schema or create a database. Personal Chinese learning notes remain in the ignored `local-work-notes/` directory and are not embedded in the formal tool.

From the repository root:

```powershell
python -B experiment-analysis/tools/prepare_database_design.py --help
python -B experiment-analysis/tools/prepare_database_design.py --output experiment-analysis/reports/database-design/new-snapshot
```

The default output is the existing `reports/database-design/2026-10-26` snapshot, so a normal rerun refuses to overwrite it. Use a new output directory to reproduce the report. `--module-root` can select an alternative input module directory. All input checks happen before the output directory is created. Checks do not establish database transaction, deduplication, or SQL correctness; these features remain unimplemented. This tool currently targets the fixed N/S snapshot, not arbitrary model collections.