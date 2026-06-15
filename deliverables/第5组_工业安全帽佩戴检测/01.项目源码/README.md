# ODPlatform — Object Detection Platform

通用目标检测工程平台 · V1.0 实训项目

> **落地场景**：工业安全帽佩戴检测 | **算法**：YOLOv8n (3.0M 参数) | **mAP50**：0.939 | **测试**：20 项全部 PASS

## 项目简介

ODPlatform 是一个与数据集解耦、与业务场景解耦的通用目标检测工程平台。V1.0 以**工业安全帽佩戴检测**为落地场景，端到端覆盖标准机器学习流水线：

```
原始数据 → 格式转换(PASCAL VOC→YOLO) → 数据验证(四维质检) → 配置管理(Pydantic v2) → 训练(YOLOv8) → 评估(mAP/P/R) → 推理(四线程流水线) → 可视化(中文字体+HUD)
```

**核心特性**：
- 🎯 **与数据集解耦**：换一个数据集只需改 `data.yaml`，无需修改业务代码
- 🔌 **与前端解耦**：OutputSink 抽象接缝，同一套推理核心支持 CLI/桌面GUI/Web 三种界面
- ⚡ **60fps+ 高帧率**：CameraSource 支持 MSMF 后端 90fps 采集（撞墙级调优）
- 🖥️ **三界面**：CLI 命令行 (8个命令) + tkinter 桌面GUI + FastAPI Web 界面
- 🔤 **中文标签**：霞鹜文楷字体 Pillow 渲染，完美支持 CJK 字符
- 📊 **HUD 面板**：实时显示 FPS/推理耗时/帧计数/检测数量
- 🚀 **TensorRT 就绪**：原生支持 `.engine` 格式直接加载推理

---

## 快速开始

### 环境要求

| 项 | 最低要求 | 推荐 |
|---|---|---|
| Python | 3.10+ | 3.10+ |
| GPU | 可选 (CPU 可运行) | RTX 3070+ (8GB+) |
| CUDA | 11.8+ | 12.1+ |
| 操作系统 | Windows 10+ / Linux | Windows 11 / Ubuntu 22.04 |

### 一键安装运行

```bash
# 1. 克隆仓库
git clone https://github.com/Ge1sT0327/ODPlatform.git
cd ODPlatform

# 2. 安装核心依赖
pip install -e apps/platform/ ultralytics opencv-python pydantic pyyaml

# 3. 安装 Web 界面依赖 (可选)
pip install fastapi uvicorn python-multipart

# 4. 初始化运行时目录
odp-init

# 5. 启动 Web 界面 (推荐演示方式)
python apps/web-backend/server.py
# 浏览器打开 http://localhost:8000

# 6. 或启动桌面 GUI
python apps/desktop/main.py

# 7. 或使用 CLI 推理
odp-infer --source samples/img_0000.jpg --show
```

### 完整流水线 (CLI 模式)

```bash
# Step 1: 准备数据集 → 放入 data/raw/<dataset_name>/
#          (需包含 JPEGImages/ 和 Annotations/ 目录，PASCAL VOC 格式)

# Step 2: 数据转换 + 切分
odp-transform --dataset safety_helmet --format pascal_voc --classes hat person

# Step 3: 数据质检
odp-validate --dataset safety_helmet --split all

# Step 4: 生成训练配置
odp-gen-config train

# Step 5: 训练 (GPU 推荐)
odp-train --model yolov8n.pt --data safety_helmet.yaml --epochs 100 --batch 16

# Step 6: 评估
odp-eval --weights models/checkpoints/exp_xxx_best.pt --data safety_helmet.yaml

# Step 7: 推理
odp-infer --source samples/img_0000.jpg --weights models/checkpoints/exp_xxx_best.pt --show
```

---

## 项目架构

### 分层架构

```
┌──────────────────────────────────────────────────────┐
│  展示层  │ CLI (8 commands) │ Desktop (tkinter) │ Web (FastAPI) │
├──────────────────────────────────────────────────────┤
│  业务层  │ training │ evaluation │ inference │ frame_source │
│          │ data_pipeline │ data_validation │ runtime_config │
│          │ visualization │
├──────────────────────────────────────────────────────┤
│  基础层  │ common (paths / logging / model / constants) │
└──────────────────────────────────────────────────────┘
```

### 模块统计

| 模块 | 行数 | 负责人 | 核心职责 |
|------|------|--------|----------|
| `inference` | 1,298 | 陈瀚鹏 | 四线程流水线 + HUD + OutputSink + CancelToken |
| `visualization` | 831 | 王智鹏 | BeautifyVisualizer + PillowTextRenderer + TextSizeCache |
| `data_pipeline` | 704 | 高文焱 | 3格式互转(PASCAL VOC/COCO/YOLO) + 切分 + 编排 |
| `frame_source` | 645 | 陈瀚鹏 | CameraSource(60fps) + Video/Image + ThreadedSource |
| `common` | 578 | 高晨曦 | 路径/日志/模型/常量/系统信息 |
| `data_validation` | 562 | 高文焱 | 四维质检(yaml/pair/label/split) + 报告 |
| `runtime_config` | 483 | 刘睿煊 | Pydantic v2 配置模型 + Generator + Merger |
| `cli` | 284 | 高晨曦 | 8 个 CLI 命令入口 |
| `training` | 161 | 刘睿煊 | TrainService 六阶段训练编排器 |
| `evaluation` | 78 | 陈瀚鹏 | ValService 评估编排器 |
| **总计** | **5,628** | **5人团队** | **94 源文件 · 20 测试** |

### 目录结构

```
ODPlatform/
├── apps/
│   ├── platform/                    # 核心引擎
│   │   ├── src/odp_platform/
│   │   │   ├── common/              # 基础设施层
│   │   │   ├── cli/                 # 8 个 CLI 命令
│   │   │   ├── data_pipeline/       # 数据流水线 (格式转换+切分)
│   │   │   ├── data_validation/     # 数据四维质检
│   │   │   ├── runtime_config/      # Pydantic v2 配置管理
│   │   │   ├── training/            # 训练编排
│   │   │   ├── evaluation/          # 模型评估
│   │   │   ├── inference/           # 推理流水线 (四线程)
│   │   │   │   ├── pipeline.py      #   ThreadedPipeline
│   │   │   │   ├── overlay.py       #   HUD 信息面板
│   │   │   │   ├── cancel.py        #   CancelToken
│   │   │   │   ├── hooks.py         #   InferHooks
│   │   │   │   └── sinks.py         #   OutputSink/NullSink/LocalFileSink
│   │   │   ├── frame_source/        # 统一帧源 (60fps 摄像头)
│   │   │   └── visualization/       # 美化绘制 + 中文字体
│   │   │       ├── visualizer.py    #   BeautifyVisualizer
│   │   │       ├── assets/          #   霞鹜文楷字体 (16MB)
│   │   │       └── core/            #   PillowTextRenderer + TextSizeCache
│   │   ├── configs/                 # 数据集 + 运行配置 YAML
│   │   └── tests/                   # 20 项测试
│   ├── desktop/
│   │   └── main.py                  # 桌面 GUI (tkinter + HUD 面板)
│   └── web-backend/
│       ├── server.py                # FastAPI + 内嵌前端 (单文件)
│       └── requirements.txt
├── deliverables/                    # 学生成果物
│   └── 第5组_工业安全帽佩戴检测/
│       ├── 01.项目源码/
│       ├── 02.项目运行录屏/
│       ├── 03.项目文件/              # 概要设计书/结合测试/分工表
│       └── 04.实训总结报告/           # 5份个人报告
├── models/checkpoints/
│   └── exp_20260614_125153_best.pt   # 训练好的模型 (6MB · mAP50=0.939)
├── samples/                          # 7 张示例图片
├── scripts/                          # CI + TensorRT 工具
└── docs/
```

---

## 实测结果

### 训练

| 指标 | 数值 |
|------|------|
| 模型 | YOLOv8n (3.0M 参数, 8.1 GFLOPs) |
| 数据集 | 7581 张, 2 类 (hat/person) |
| 训练环境 | NVIDIA RTX 4090 (24GB) |
| 训练参数 | epochs=100, batch=16, imgsz=640 |
| 训练耗时 | ≈35 分钟 (≈20s/epoch) |
| **mAP50** | **0.939** |
| **mAP50-95** | **0.616** |
| 模型大小 | 6.0 MB |

### 评估 (验证集 758 张)

| 指标 | 数值 |
|------|------|
| mAP50 | 0.936 |
| Precision | 0.937 |
| Recall | 0.895 |
| hat 类 mAP50 | 0.932 |
| person 类 mAP50 | 0.940 |

### 推理性能 (RTX 3070)

| 模式 | 耗时 |
|------|------|
| 单帧图片推理 | 7-13ms |
| Web 实时摄像头 | 15-20 FPS |
| TensorRT 引擎 | loop 80+ FPS |

### 数据质检

```
ERROR=0  WARNING=0  INFO=4
格式转换成功率: 100% (7581/7581)
图片-标注配对率: 100%
切分重叠率: 0%
```

### 测试

```
20 项测试全部 PASS
├── 单元测试: 12 项 (paths/logging/config/convert/string_utils/frame_source)
├── 集成测试: 6 项 (e2e_smoke/validate/frame_source)
└── 端到端测试: 2 项 (训练100epoch + 评估 + 推理)
```

---

## CLI 命令参考

| 命令 | 功能 | 示例 |
|------|------|------|
| `odp-init` | 初始化运行时目录 | `odp-init` |
| `odp-reset` | 清理运行时产物 | `odp-reset` |
| `odp-transform` | 数据转换+切分 | `odp-transform --dataset safety_helmet --format pascal_voc --classes hat person` |
| `odp-validate` | 四维数据质检 | `odp-validate --dataset safety_helmet --split all` |
| `odp-gen-config` | 生成配置 YAML 模板 | `odp-gen-config train` |
| `odp-train` | YOLO 模型训练 | `odp-train --model yolov8n.pt --data safety_helmet.yaml --epochs 100 --batch 16` |
| `odp-eval` | 模型评估 | `odp-eval --weights best.pt --data safety_helmet.yaml` |
| `odp-infer` | 推理 | `odp-infer --source 0 --weights best.pt --show` |

---

## 三种界面

### 1. Web 界面 (推荐演示)
```bash
pip install fastapi uvicorn python-multipart
python apps/web-backend/server.py
# 浏览器 → http://localhost:8000
```
- 实时摄像头 WebSocket 逐帧推理
- 图片拖拽上传即时检测
- 视频文件本地解码实时推理
- 深色主题 + 右侧统计面板

### 2. 桌面 GUI
```bash
python apps/desktop/main.py
```
- tkinter 深色主题窗口
- 摄像头/图片/视频三种输入模式
- HUD 面板实时显示 FPS·推理耗时·帧号·检测数

### 3. CLI 命令行
```bash
odp-infer --source samples/img_0000.jpg --show
```
- 摄像头实时检测 (`--source 0`)
- 图片/视频离线推理
- 按键交互 (q退出/s截图/m中英切换/d框开关/f面板开关)

---

## 团队

| 姓名 | 角色 | 负责模块 |
|------|------|----------|
| 高晨曦 | 架构师 | common + 整体架构 + CI/CD + 代码规范 |
| 高文焱 | 数据工程师 | data_pipeline + data_validation |
| 刘睿煊 | 算法工程师A | runtime_config + training |
| 陈瀚鹏 | 算法工程师B | evaluation + inference + frame_source |
| 王智鹏 | 应用工程师 | visualization + desktop + web-backend |

指导教师：雨霓

---

## 技术亮点

### 60fps+ 高帧率摄像头 (撞墙记录)
```python
# CameraConfig 支持 90fps
config = CameraConfig(width=1280, height=720, fps=90, backend="msmf")

# 三大关键点 (踩坑总结):
# 1. MSMF 必须在 VideoCapture 创建前设置环境变量
#    os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
# 2. 参数顺序: 分辨率 → FOURCC → FPS (不能乱!)
# 3. set() 后必须 read() 触发硬件协商, 再 get() 读回实际值
```

### OutputSink 抽象接缝
```python
class OutputSink(ABC):
    def open(self, output_dir, source_type) -> None: ...
    def write(self, frame, annotated) -> None: ...
    def close(self) -> None: ...

# 推理核心零前端依赖 — 三端共享同一推理引擎
```

### TensorRT 部署
```bash
# 导出 TensorRT 引擎
yolo export model=best.pt format=engine batch=1 device=0

# 直接用 — 代码零改动
odp-infer --source 0 --model best.engine

# trtexec 裸引擎补元数据
python scripts/wrap_trt_engine.py --pt best.pt --raw raw.engine --out wrapped.engine
```

---

## 贡献指南

详见 [CONTRIBUTING.md](./CONTRIBUTING.md)

- 分支策略：feature 分支 → PR → main
- 提交规范：Conventional Commits (`feat:`/`fix:`/`docs:`/`refactor:`)
- 代码风格：ruff 格式化
- 架构约束：业务模块只向下依赖 common (CON-06)
- 路径规范：所有路径走 common.paths (CON-05)

---

## 许可证

MIT License
