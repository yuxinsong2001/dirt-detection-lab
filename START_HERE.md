# 仓库导航：先看这里

本项目包含原有 YOLO 检测实验和正在开发的实验数据分析工具。不要把个人讲解、原始实验、程序输出混为一类。

**本次新增的工作全部集中在 [experiment-analysis](experiment-analysis/README.md)。先打开它的 README，就能看到程序、测试、输出和说明各在哪里。**

本次仓库整理结果见 [验证记录](docs/organization-validation.md)。VS Code 仅在界面隐藏环境和第三方目录，没有删除它们；可在工作区设置的 files.exclude 中重新显示。

## 我要找什么？

| 你要找的内容 | 位置 | 说明 |
|---|---|---|
| 项目背景与训练方法 | [README.md](README.md) | 原项目介绍和复现命令。 |
| 本次开发的讲解、德语术语、面试追问 | experiment-analysis/local-work-notes/README.md | 仅本地保留；GitHub 中没有这些个人说明。 |
| 原项目 Python 工具 | [scripts](scripts/README.md) | 正式实现；tools 和根目录旧命令保留兼容入口。 |
| 新增代码与测试 | [experiment-analysis](experiment-analysis/README.md) | 统一模块入口。 |
| 训练及评估原始记录 | [runs](runs) | 平铺训练目录已归入 runs/detect/training；test 和演示目录独立保留。 |
| 最新清点结果 | experiment-analysis/reports/inventory/experiment_inventory_2026-10-24_grouped.json | 新模块内部的程序输出；原 JSON 保留作旧快照。 |
| 最终报告 PDF | [reports/pdf](reports/pdf) | 正式PDF；旧稿与预览归入 reports/archive。 |
| 演示文稿、讲稿 | [reports/presentations](reports/presentations) | PPTX、演示 PDF、Word 讲稿。 |
| 报告源文件 | [reports/sources](reports/sources) | LaTeX 源文件。 |
| 实验分析记录 | [reports/experiments](reports/experiments) | 详细报告、训练总结和结果分析统一存放。 |
| 标签预览图 | reports/figures/multiclass_label_qa/ | 图像标注质量检查的程序输出。 |
| 所有报告与总结 | [reports/README.md](reports/README.md) | 实验总结、结果分析、PDF 和演示文稿的统一入口。 |
| 运行指南 | [docs](docs) | 数据路径配置与训练执行指南，不放结果分析报告。 |
| 数据配置 | [cfg](cfg) | cfg/local 是仅本机使用的数据路径配置。 |
| 图像与标签 | data/、datasets/ | 保留原路径，避免影响配置和数据链接。 |
| 模型参数 | weights/、根目录 *.pt、runs 中的 weights | 保留原位置；根目录权重可被现有 YOLO 命令直接使用。 |

## 日常主要看这些目录

```text
DirtNet_Project/
  START_HERE.md             ← 找东西的入口
  README.md                 ← 原项目背景与运行说明
  scripts/                  ← 原项目工具正式实现
  tools/                    ← 原命令的兼容入口
  logs/                     ← 运行日志
  archive/                  ← 旧源码下载包
  experiment-analysis/      ← 本次新增工作的总目录
    README.md               ← 模块介绍和运行入口
    tools/                  ← 实验清点等新增代码
    tests/                  ← 新增程序测试
    reports/inventory/      ← 新增程序输出 JSON
    local-work-notes/       ← 不上传的学习说明、历史资料与整理记录
  cfg/                      ← 配置
  runs/                     ← 原始实验记录，detect/training 为归类后的训练目录
  reports/
    experiments/            ← 实验分析报告
    pdf/                    ← 正式报告 PDF
    archive/                ← 旧报告与排版预览，本地保留
    presentations/          ← 演示文稿和讲稿
    sources/                ← 报告源文件
    figures/                ← 生成的预览图片
  docs/                     ← 项目技术文档
```

## 暂不移动的基础设施

`.git` 是 Git 历史，`.venv` 是 Python 环境；`.codex`、`.agents`、`.worktrees` 是开发工具目录。`Ultralytics`、`ultralytics-repo`、`yolov3-master` 暂不移动；当前环境直接导入 ultralytics-repo。旧源码压缩包已归入 archive/source-downloads，根目录日志移入 logs。tmp 暂时保留，不删除。

根目录 YAML 和数据转换脚本仍可按原方法使用。后续按用户要求，37个平铺训练目录已归入 runs/detect/training；使用这些目录中的权重时需采用新路径。历史 args.yaml/opt.yaml 保留当时实际执行路径，不作为当前路径指南。

## 后续文件约定

- 个人讲解只进 experiment-analysis/local-work-notes/steps。
- 新模块的结果只进 experiment-analysis/reports/<功能名>/。
- 新训练输出统一指定 project=runs/detect/training；保留各实验自己的名称。测试评估仍在 runs/detect/test。
- 本次新增程序和测试都在 experiment-analysis 内部，不继续散放到根目录 tools、tests。
- 在根目录运行命令；已有输出需另取新文件名，清点工具不会覆盖旧 JSON。

```powershell
python experiment-analysis/tools/inventory_experiments.py --output experiment-analysis/reports/inventory/inventory-new.json
python -m unittest discover -s experiment-analysis/tests -p test_inventory_experiments.py -v
```

目录调整与新增分析功能分批提交到本地 Git，尚未推送。忽略目录不是备份，请另行保管个人学习资料。
