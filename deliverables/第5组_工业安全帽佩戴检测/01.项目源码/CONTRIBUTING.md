# ODPlatform 协作规范

## 分支策略

每个角色在独立的 feature 分支上开发，通过 PR 合入主分支。

| 分支名 | 角色 | 负责模块 |
|---|---|---|
| `main` | — | 受保护，仅通过 PR 合入 |
| `feat/common` | 架构师 | `common/` + CI 守门 + ADR |
| `feat/data` | 数据工程师 | `data_pipeline/` + `data_validation/` |
| `feat/config-training` | 算法工程师 A | `runtime_config/` + `training/` |
| `feat/eval-inference` | 算法工程师 B | `evaluation/` + `inference/` + `frame_source/` |
| `feat/visual-desktop` | 应用工程师 | `visualization/` + `apps/desktop/` |

## 开发流程

### 1. 创建你的 feature 分支

```bash
git checkout main
git pull origin main
git checkout -b feat/<你的分支名>
```

### 2. 提交规范

遵循 [约定式提交（Conventional Commits）](https://www.conventionalcommits.org/)：

```
feat(common): add paths.py with marker-file ROOT_DIR location
feat(data_validation): add yaml_schema check
fix(inference): resolve frame drop on camera disconnect
test(training): add unit tests for TrainService
docs(architecture): add ADR-001 documenting Monorepo decision
chore: update .gitignore for logging directory
```

每次 commit 对应一个完整里程碑，**不要**在历史中留"先写错再修复"的废提交。

### 3. 提交 PR

```bash
git push origin feat/<你的分支名>
```

然后在 GitHub 上创建 Pull Request，填写 PR 模板。

### 4. 代码评审

- 架构师负责**评审全部 PR**（关注依赖纪律、路径规范、接口契约）
- 各角色之间在交接节点互相确认接口兼容性
- 所有 CI 守门脚本**必须通过**才能合入

## 核心架构约束（不可违反）

这些规则由 CI 脚本自动校验，违反即构建失败：

| 约束 | 编号 | 检查方式 |
|---|---|---|
| 只向下依赖 common，不反向、不横向 | CON-06 | grep：推理/评估包内 `import training` 命中数为 0 |
| 路径统一走 `paths.py`，无硬编码 | CON-05 | grep 扫描绝对/相对路径硬编码 |
| 业务模块无 `print` 调试 | NFR-OBS-01 | grep 扫描 `print(` |
| 对外 API 通过 `__all__` 声明 | NFR-ENG-04 | 检查 `__init__.py` |
| 可移植模块零宿主依赖 | CON-08 | grep：frame_source/visualization 内 `import odp_platform` 命中数为 0 |
| 推理包无前端框架依赖 | NFR-EXT-03 | grep：inference/ 内 `import PyQt|FastAPI|Celery` 命中数为 0 |

## 交接链

团队之间通过标准交接物串联，接口签名冻结后不可擅自变更：

| 节点 | 上游 | 下游 | 交接物 |
|---|---|---|---|
| ① | 数据工程师 | 算法工程师 A | 标准 YOLO 数据集 + `data.yaml`（通过质检） |
| ② | 算法工程师 A | 算法工程师 B | 归档 `best.pt` + 类别信息 + 预处理约定（写入 audit） |
| ③ | 算法工程师 B | 应用工程师 | `InferService` 推理引擎（经 `OutputSink` 接缝接入） |

## 代码风格

- Python 3.11+，type hints 推荐使用
- 格式化：ruff（配置见 `pyproject.toml`）
- 行宽：100 字符
- 引号：双引号
- 缩进：4 空格

运行前格式化：

```bash
pip install ruff
ruff check apps/platform/src/
ruff format apps/platform/src/
```

## 文档规范

- 每个子系统须有对应 ADR，存放于 `docs/architecture/`
- ADR 格式：[背景、决策、备选方案、后果（代价）、状态]
- ADR 编号连续、不可删除，被推翻时标记为 Superseded 并指向新 ADR
