# ODPlatform — Object Detection Platform

通用目标检测工程平台 · V1.0 实训项目

## 项目简介

ODPlatform 是一个与数据集解耦、与业务场景解耦的通用目标检测工程平台。
V1.0 以**RSOD 遥感目标检测**为落地场景，采用 YOLO 系列模型，端到端覆盖：

```
原始数据 → 格式转换 → 数据验证 → 配置管理 → 训练 → 评估 → 推理 → 可视化
```

## 技术栈

| 层面 | 技术 |
|---|---|
| 语言 | Python 3.11+ |
| 深度学习 | PyTorch + Ultralytics (YOLO) |
| 图像处理 | OpenCV |
| 配置校验 | Pydantic v2 |
| 桌面端 | PyQt |
| 测试 | pytest |

## 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/你的用户名/ODPlatform.git
cd ODPlatform

# 2. 安装依赖
pip install -e apps/platform/

# 3. 初始化运行时目录
odp-init

# 4. 下载 RSOD 数据集 → 放至 data/raw/ 目录

# 5. 端到端运行
odp-transform --dataset rsod
odp-validate  --dataset rsod --split all
odp-gen-config train
odp-train     --config train.yaml
odp-eval      --weights <归档的 best.pt>
odp-infer     --source 0 --show
```

## 团队分工

| 角色 | 负责模块 | 分支 |
|---|---|---|
| 架构师 | `common/` + CI 守门 + ADR | `feat/common` |
| 数据工程师 | `data_pipeline/` + `data_validation/` | `feat/data` |
| 算法工程师 A | `runtime_config/` + `training/` | `feat/config-training` |
| 算法工程师 B | `evaluation/` + `inference/` + `frame_source/` | `feat/eval-inference` |
| 应用工程师 | `visualization/` + `apps/desktop/` | `feat/visual-desktop` |

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

## 操作注意事项

### 环境要求
- Python 3.11+
- 建议使用虚拟环境（venv / conda）
- GPU 环境需安装 CUDA 版 PyTorch（CPU 亦可降级运行）

### 依赖安装
```bash
# 最小安装（仅平台核心）
pip install -e apps/platform/

# 含测试依赖
pip install -e "apps/platform/[test]"

# 含开发依赖（ruff、mypy）
pip install -e "apps/platform/[dev,test]"
```

### 开发规范
- **分支策略**：每人工作在独立 feature 分支，通过 PR 合入 `main`
- **提交规范**：遵循约定式提交（Conventional Commits），格式 `feat(scope): 描述`
- **代码风格**：ruff 格式化，行宽 100，双引号，4 空格缩进
- **依赖纪律**：业务模块只向下依赖 `common`，不反向、不横向耦合
- **路径规范**：所有路径走 `common.paths`，禁止硬编码
- **日志规范**：使用 `get_logger`，禁止 `print` 做业务日志
- **API 规范**：对外公共 API 必须经 `__init__.py` 的 `__all__` 声明

### 提交前检查
```bash
ruff format apps/platform/src/
ruff check apps/platform/src/
pytest apps/platform/tests/
```

### 关键架构约束（不可违反）
| 约束 | 编号 | 检查方式 |
|---|---|---|
| 只向下依赖 common，不反向、不横向 | CON-06 | CI grep 守门 |
| 路径统一走 `paths.py`，无硬编码 | CON-05 | CI grep 守门 |
| 业务模块无 `print` 调试 | NFR-OBS-01 | CI grep 守门 |
| 对外 API 通过 `__all__` 声明 | NFR-ENG-04 | 检查 `__init__.py` |
| 可移植模块零宿主依赖 | CON-08 | CI grep 守门 |
| 推理包无前端框架依赖 | NFR-EXT-03 | CI grep 守门 |

### 交接链
| 节点 | 上游 | 下游 | 交接物 |
|---|---|---|---|
| ① | 数据工程师 | 算法工程师 A | 标准 YOLO 数据集 + `data.yaml`（通过质检） |
| ② | 算法工程师 A | 算法工程师 B | 归档 `best.pt` + 类别信息 + 预处理约定 |
| ③ | 算法工程师 B | 应用工程师 | `InferService` 推理引擎（经 `OutputSink` 接缝接入） |

## 数据集

本 V1.0 使用 **RSOD 遥感目标检测数据集**：

- **简介**：RSOD（Remote Sensing Object Detection）是一个公开的遥感图像目标检测数据集
- **类别**：aircraft / oiltank / overpass / playground
- **原始格式**：PASCAL VOC

> 平台与数据集解耦——将 `data.yaml` 指向其他目标检测数据集后，全链路无需修改业务代码。

## 目录结构

```
ODPlatform/
├── apps/
│   ├── platform/
│   │   ├── pyproject.toml
│   │   ├── src/odp_platform/
│   │   │   ├── common/             # 基础层（架构师）
│   │   │   ├── data_pipeline/      # 数据流水线（数据工程师）
│   │   │   ├── data_validation/    # 数据验证（数据工程师）
│   │   │   ├── runtime_config/     # 运行配置（算法工程师 A）
│   │   │   ├── training/           # 训练编排（算法工程师 A）
│   │   │   ├── evaluation/         # 评估（算法工程师 B）
│   │   │   ├── inference/          # 推理流水线（算法工程师 B）
│   │   │   ├── frame_source/       # 统一帧源（算法工程师 B）
│   │   │   ├── visualization/      # 可视化（应用工程师）
│   │   │   └── cli/                # 命令行入口（架构师 + 各角色）
│   │   ├── configs/
│   │   │   ├── datasets/           # 数据集配置
│   │   │   └── runtime/            # 运行配置模板
│   │   ├── tests/                  # 测试
│   │   └── logging/                # 运行时日志（不入库）
│   └── desktop/                    # 桌面端 GUI（应用工程师）
├── docs/
│   └── architecture/               # ADR 架构决策记录
├── .github/                        # PR 模板
├── .odp-workspace                  # 工作区标记文件
├── .gitignore
├── pyproject.toml
├── README.md
└── CONTRIBUTING.md
```

## 里程碑时间线

| 里程碑 | 内容 | 建议工期 | 分支 |
|---|---|---|---|
| M0 | 仓库骨架 + 架构基线 | 第 1 周 | `main` |
| M1 | `common/` 基础层 + `odp-init/reset` | 第 2-3 周 | `feat/common` |
| M2 | `data_pipeline/` + `data_validation/` | 第 3-4 周 | `feat/data` |
| M3 | `runtime_config/` | 第 3-4 周 | `feat/config-training` |
| M4 | `training/` + `evaluation/` | 第 5-6 周 | `feat/config-training` + `feat/eval-inference` |
| M5 | `frame_source/` + `inference/` + `visualization/` + `desktop/` | 第 6-8 周 | `feat/eval-inference` + `feat/visual-desktop` |

> M2 和 M3 可并行开发。M4 依赖 M2+M3。M5 依赖 M4。

## 需求文档

- [ODP-PRD-001 产品需求文档（总纲）](./docs/ODP-PRD-001_产品需求文档_总纲.md)
- [ODP-SRS-01 common 需求规格](./docs/ODP-SRS-01_common_需求规格.md)
- [ODP-SRS-03 data_validation 需求规格](./docs/ODP-SRS-03_data_validation_需求规格.md)
- [ODP-SRS-04 runtime_config 需求规格](./docs/ODP-SRS-04_runtime_config_需求规格.md)
- [ODP-SRS-05 training 需求规格](./docs/ODP-SRS-05_training_需求规格.md)
- [ODP-SRS-06 evaluation 需求规格](./docs/ODP-SRS-06_evaluation_需求规格.md)

## 许可证

MIT License
