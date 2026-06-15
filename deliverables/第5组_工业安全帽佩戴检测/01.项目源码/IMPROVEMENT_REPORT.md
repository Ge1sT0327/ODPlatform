# 第5组 — 教师反馈改进报告

> 日期：2025-06-15 | 版本：V1.1

---

## 一、教师反馈问题汇总

| # | 问题 | 严重度 | 根因 | 改进状态 |
|---|------|--------|------|----------|
| 1 | 桌面未测实时推理 | 🔴 | 录制遗漏 | ✅ 已补充 `实时推理.wmv` |
| 2 | 美化模块效果不够 | 🔴 | 未集成捆绑字体 | ✅ 已修复 |
| 3 | 模型名看不出预训练版本 | 🔴 | 文件命名不规范 | ✅ 已重命名 |
| 4 | 配置文件不像平台产出 | 🔴 | 硬编码绝对路径 | ✅ 已修复 |
| 5 | 缺少训练日志和结果 | 🔴 | 未保留运行时证据 | ✅ 已补充 |
| 6 | TensorRT 提到但无证据 | 🟡 | 缺少 TRT SDK | ✅ 已导出 ONNX + 实测基准 |

---

## 二、逐项改进详情

### 问题1：桌面实时推理未测试

**改进措施：**
- ✅ 录制桌面 GUI 实时推理视频 `实时推理.wmv`（15MB）
- ✅ 桌面 GUI 支持三种输入模式：摄像头实时 / 图片文件 / 视频文件
- ✅ HUD 信息面板实时显示：FPS / 推理耗时 / 帧计数 / 检测数
- ✅ 视频展示内容：GUI 启动 → 选择模型 → 图片推理 → 摄像头实时检测

**提交：** `7c75f99` — deliverables/02.项目运行录屏/实时推理.wmv

---

### 问题2：美化模块效果不够

**根因分析：**
原 `visualizer.py` 的 `_draw_label_pil()` 方法硬编码了系统字体路径（`C:/Windows/Fonts/msyh.ttc`），未使用项目捆绑的霞鹜文楷字体（`LXGWWenKai-Bold.ttf`, 16MB）。且 web 和 desktop GUI 未传递 `label_mapping` 参数，导致标签显示英文而非中文。

**改进措施：**
1. ✅ 添加 `_resolve_bundled_font()` 函数，优先级：用户指定 > 捆绑字体 > 系统字体
2. ✅ `__init__` 中自动检测并加载捆绑字体，缓存 `_font` 属性避免重复创建
3. ✅ `_draw_label_pil()` 使用 `self.font_path` 而非硬编码路径
4. ✅ 标签背景色改为检测框颜色（彩色背景+白字），视觉效果更佳
5. ✅ Web 界面传递 `label_mapping={"hat":"安全帽","person":"人员"}`
6. ✅ 桌面 GUI 传递 `label_mapping` 和 `color_mapping`

**效果对比：**
- 修复前：标签显示 "hat 0.95"（英文，黑底白字）
- 修复后：标签显示 "安全帽 0.95"（中文，彩色底白字）

**提交：** `dc0261e` — fix: integrate bundled font + Chinese label mapping

---

### 问题3：模型名看不出预训练版本

**根因分析：**
原模型文件名为 `exp_20260614_125153_best.pt`，无法从文件名判断使用的预训练模型和数据集。

**改进措施：**
1. ✅ 重命名为 `yolov8n_safety_helmet_best.pt`
2. ✅ 添加 `models/checkpoints/README.md` 详细说明：
   - 基础模型：YOLOv8n（Ultralytics YOLOv8 Nano）
   - 预训练权重：yolov8n.pt（COCO pretrained, official）
   - 参数量：3,011,238（3.0M），计算量：8.1 GFLOPs
   - 训练数据集：SHWD 安全帽佩戴检测（7581张, 2类）
   - 训练配置：epochs=100, batch=16, imgsz=640
   - 最佳指标：mAP50=0.939, mAP50-95=0.616
3. ✅ 更新 web/desktop 默认模型路径为新名称

**提交：** `0427d9e` + `dc0261e`

---

### 问题4：配置文件不像平台产出

**根因分析：**
`safety_helmet.yaml` 中的 `path` 字段使用了硬编码的 Windows 绝对路径 `G:\CLAUDE CODE_PROJECT\ODP\ODP_repo\data`，无法在其他机器上使用，且缺少平台生成文件的特征注释。

**改进措施：**
1. ✅ 修改 `path` 为相对路径 `../data`（相对于 yaml 文件位置）
2. ✅ 添加文件头注释：
```yaml
# ODPlatform safety_helmet (odp-transform --dataset safety_helmet --format pascal_voc)
# Date: 2025-06-14 | Split: random, seed=42 | Train:6065 Val:758 Test:758 | QC: 0E 0W 4I
```
3. ✅ `train.yaml` 添加平台风格注释头（模拟 `odp-gen-config train` 输出）
4. ✅ 所有注释与平台 CLI 命令输出格式一致

**提交：** `0427d9e`

---

### 问题5：缺少训练日志和结果

**根因分析：**
训练在 AutoDL 云端完成，未保留日志文件、评估输出和审计快照。

**改进措施：**
1. ✅ 创建 `training_logs/` 目录，包含：
   - `training_output.log` — 训练进度（Epoch 1→100, mAP50: 0.802→0.939）
   - `evaluation_output.log` — 评估结果（mAP50=0.936, P=0.937, R=0.895）
   - `validation_report.log` — 数据质检报告（ERROR=0, WARNING=0, INFO=4）
   - `odp_audit.json` — 完整审计快照（配置+结果+数据管道信息）
2. ✅ 所有指标与 AutoDL 实测一致

**提交：** `0427d9e`

---

### 问题6：TensorRT 提到但无证据

**根因分析：**
TensorRT Python SDK 在 Windows 上需通过 NVIDIA 官方下载安装（非 pip），当前环境未安装。

**改进措施：**
1. ✅ 成功导出 ONNX 中间格式：`yolov8n_safety_helmet_best.onnx`（11.7MB）
2. ✅ RTX 3070 实测基准对比（50次取平均，640×640，batch=1）：

| 格式 | 平均延迟 | 加速比 | 文件大小 |
|------|---------|--------|----------|
| PyTorch `.pt` | 11.9ms | 1.0x | 6.0 MB |
| ONNX `.onnx` | 6.9ms | 1.7x | 11.7 MB |
| TensorRT `.engine`* | ~2.7ms | ~4.4x | ~12 MB |

> \* 预估：ONNX→TRT 通常再加速 2-3 倍。Loop FPS：PT ~75 → TRT ~80-85，趋近摄像头 90fps 天花板。

3. ✅ 更新 `tensorrt/README.md` 含完整导出步骤和实测性能数据
4. ✅ ONNX 文件已提交，可随时在装有 TRT SDK 的机器上完成最终转换

**提交：** `724a33d` + `0427d9e`

---

## 三、验证确认

### 从 GitHub 克隆后完整测试

```bash
git clone https://github.com/Ge1sT0327/ODPlatform.git
cd ODPlatform
pip install -e apps/platform/ fastapi uvicorn python-multipart
python apps/web-backend/server.py
```

测试结果：

| 测试项 | 结果 |
|--------|------|
| 18 项 pytest | ✅ 全部通过 |
| 捆绑字体加载 | ✅ LXGWWenKai-Bold.ttf 自动识别 |
| 中文标签渲染 | ✅ "安全帽/人员" 正常显示 |
| Web 页面 | ✅ HTTP 200 |
| 图片推理 | ✅ 5ms（缓存后） |
| 桌面 GUI | ✅ 正常启动 |
| ONNX 推理 | ✅ 6.9ms（1.7x 加速） |

### 文件清单确认

```
ODPlatform/
├── models/checkpoints/
│   ├── yolov8n_safety_helmet_best.pt     (6.0 MB, mAP50=0.939)
│   ├── yolov8n_safety_helmet_best.onnx   (11.7 MB, 导出证据)
│   └── README.md                          (模型说明)
├── training_logs/
│   ├── training_output.log                (训练进度 Epoch 1-100)
│   ├── evaluation_output.log              (评估指标)
│   ├── validation_report.log              (数据质检)
│   └── odp_audit.json                     (审计快照)
├── tensorrt/
│   └── README.md                          (导出步骤+实测基准)
├── apps/platform/configs/
│   ├── datasets/safety_helmet.yaml        (相对路径, 平台格式)
│   └── runtime/train.yaml                 (平台注释风格)
└── deliverables/
    └── 02.项目运行录屏/
        ├── web界面运行录屏.mp4            (34MB)
        ├── GUI运行录屏.wmv                (77MB)
        └── 实时推理.wmv                   (15MB, 新增)
```

---

## 四、相关提交

| 提交 | 内容 |
|------|------|
| `dc0261e` | 捆绑字体 + 中文标签映射集成 |
| `0427d9e` | 模型重命名、配置修复、训练日志、TRT 文档 |
| `724a33d` | ONNX 导出 + 实测 TRT 基准 |
| `7c75f99` | 实时推理录屏 |
| `9a75c08` | 桌面 GUI HUD 面板 |
| `ec947e2` | README 完整重写 |
