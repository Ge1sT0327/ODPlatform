"""ODPlatform Web 界面 — FastAPI 后端 + 内嵌前端。"""

import sys
from pathlib import Path

# 将仓库根加入 sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

import asyncio
import base64
import json
import time
from io import BytesIO
from typing import Optional

import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import HTMLResponse

from odp_platform.common.model_utils import resolve_model_path
from odp_platform.visualization.visualizer import BeautifyVisualizer, Detection, DrawStyle

# ── 模型缓存 ──────────────────────────────────────────────
_model = None
_model_path: Optional[str] = None
_class_names = ["hat", "person"]
_device = "cpu"


def _get_device() -> str:
    import torch
    return "0" if torch.cuda.is_available() else "cpu"


def _load_model(path: str):
    global _model, _model_path, _class_names, _device
    _device = _get_device()
    resolved = resolve_model_path(path)
    from ultralytics import YOLO
    _model = YOLO(str(resolved))
    _model_path = path
    _class_names = [v for k, v in sorted(_model.names.items())]
    return _model


def _ensure_model(path: str = None):
    global _model, _class_names
    default = "models/checkpoints/exp_20260614_125153_best.pt"
    target = path or default
    if _model is not None and _model_path == target:
        return _model, _class_names
    return _load_model(target), _class_names


# ── 推理 ──────────────────────────────────────────────────
def _run_detection(image: np.ndarray, conf: float = 0.25, model_path: str = None):
    model, names = _ensure_model(model_path)
    results = model(image, conf=conf, iou=0.7, imgsz=640, device=_device, verbose=False)
    detections = []
    if results and results[0].boxes:
        for box in results[0].boxes:
            detections.append({
                "bbox": [round(v, 1) for v in box.xyxy[0].tolist()],
                "class_id": int(box.cls[0]),
                "class_name": names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 3),
            })
    return detections


def _draw_and_encode(image: np.ndarray, detections: list[dict]):
    viz = BeautifyVisualizer(class_names=_class_names)
    viz_dets = [Detection(
        bbox=tuple(d["bbox"]),
        class_id=d["class_id"],
        class_name=d["class_name"],
        confidence=d["confidence"],
    ) for d in detections]
    result = np.copy(image)
    viz.draw(result, viz_dets)
    ok, buf = cv2.imencode(".jpg", result, [cv2.IMWRITE_JPEG_QUALITY, 85])
    return base64.b64encode(buf).decode() if ok else ""


def _counts(detections: list[dict]) -> dict:
    c = {}
    for d in detections:
        n = d["class_name"]
        c[n] = c.get(n, 0) + 1
    return c


# ── App ───────────────────────────────────────────────────
app = FastAPI(title="ODPlatform Web")


@app.get("/", response_class=HTMLResponse)
async def index():
    return FRONTEND_HTML


@app.post("/infer/image")
async def infer_image(
    file: UploadFile = File(...),
    conf: float = Form(0.25),
    model_path: str = Form(""),
):
    try:
        data = await file.read()
        img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return {"success": False, "error": "无法解码图片"}
        t0 = time.perf_counter()
        detections = _run_detection(img, conf=conf,
                                    model_path=model_path or None)
        elapsed = (time.perf_counter() - t0) * 1000
        b64 = _draw_and_encode(img, detections)
        return {
            "success": True,
            "image": f"data:image/jpeg;base64,{b64}",
            "width": img.shape[1],
            "height": img.shape[0],
            "detections": detections,
            "counts": _counts(detections),
            "inference_time_ms": round(elapsed, 1),
        }
    except FileNotFoundError as e:
        return {"success": False, "error": str(e)}
    except Exception as e:
        return {"success": False, "error": f"推理失败: {e}"}


@app.websocket("/ws/realtime")
async def ws_realtime(ws: WebSocket):
    await ws.accept()
    conf = 0.25
    model_path = ""
    try:
        _ensure_model(model_path or None)
        await ws.send_text(json.dumps({
            "status": "ready", "classes": _class_names,
            "device": _device,
        }))

        frame_times = []
        while True:
            msg = await ws.receive()
            if "text" in msg:
                init = json.loads(msg["text"])
                conf = float(init.get("conf", 0.25))
                model_path = init.get("model", "")
                _ensure_model(model_path or None)
                continue
            if "bytes" not in msg:
                continue

            data = msg["bytes"]
            img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
            if img is None:
                continue

            t0 = time.perf_counter()
            detections = _run_detection(img, conf=conf,
                                        model_path=model_path or None)
            elapsed = (time.perf_counter() - t0) * 1000
            b64 = _draw_and_encode(img, detections)

            frame_times.append(elapsed)
            if len(frame_times) > 30:
                frame_times.pop(0)
            fps = 1000 / (sum(frame_times) / len(frame_times)) if frame_times else 0

            await ws.send_text(json.dumps({
                "image": f"data:image/jpeg;base64,{b64}",
                "detections": detections,
                "counts": _counts(detections),
                "inference_time_ms": round(elapsed, 1),
                "fps": round(fps, 1),
            }))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_text(json.dumps({"error": str(e)}))
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════
#  FRONTEND — 内嵌 HTML/CSS/JS
# ═══════════════════════════════════════════════════════════

FRONTEND_HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ODPlatform — 安全帽检测</title>
<style>
:root {
  --bg: #0f0f1a;
  --card: #1a1a2e;
  --card2: #16213e;
  --accent: #00d4ff;
  --accent2: #00d4a0;
  --text: #e0e0e0;
  --text2: #888;
  --danger: #e74c3c;
  --radius: 12px;
  --font: "Microsoft YaHei", "PingFang SC", system-ui, sans-serif;
}
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:var(--font); background:var(--bg); color:var(--text); height:100vh; display:flex; flex-direction:column; overflow:hidden; }

.header {
  background:linear-gradient(135deg, #1a1a2e, #16213e);
  padding:12px 24px; display:flex; align-items:center; gap:16px;
  border-bottom:1px solid rgba(255,255,255,0.06);
}
.header h1 { font-size:20px; font-weight:600; background:linear-gradient(90deg, var(--accent), var(--accent2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.header .badge { font-size:11px; background:var(--accent); color:#000; padding:3px 10px; border-radius:20px; font-weight:600; }
.header .device-badge { font-size:11px; background:#333; color:var(--accent2); padding:3px 10px; border-radius:20px; margin-left:auto; }

.main { display:flex; flex:1; overflow:hidden; }
.display { flex:1; display:flex; align-items:center; justify-content:center; background:#0a0a14; position:relative; min-width:0; }
.display img { max-width:100%; max-height:100%; object-fit:contain; border-radius:4px; }
.display .placeholder { color:var(--text2); font-size:16px; text-align:center; }
.display .placeholder .icon { font-size:64px; margin-bottom:16px; opacity:0.3; }

.sidebar { width:320px; background:var(--card); display:flex; flex-direction:column; border-left:1px solid rgba(255,255,255,0.06); overflow-y:auto; }
.sidebar section { padding:16px 20px; border-bottom:1px solid rgba(255,255,255,0.05); }
.sidebar h3 { font-size:13px; text-transform:uppercase; letter-spacing:1px; color:var(--text2); margin-bottom:12px; }

.mode-group { display:flex; gap:8px; }
.mode-btn { flex:1; padding:10px; border:1px solid rgba(255,255,255,0.1); background:transparent; color:var(--text); border-radius:8px; cursor:pointer; font-family:var(--font); font-size:13px; transition:all .2s; text-align:center; }
.mode-btn:hover { border-color:var(--accent); }
.mode-btn.active { background:var(--accent); color:#000; border-color:var(--accent); font-weight:600; }

.btn { width:100%; padding:12px; border:none; border-radius:8px; font-family:var(--font); font-size:14px; font-weight:600; cursor:pointer; transition:all .2s; }
.btn-start { background:linear-gradient(135deg, var(--accent), #0099cc); color:#000; }
.btn-start:hover { opacity:0.9; transform:translateY(-1px); }
.btn-start:disabled { opacity:0.4; cursor:not-allowed; transform:none; }
.btn-stop { background:var(--danger); color:#fff; }

.slider-group { display:flex; align-items:center; gap:10px; }
.slider-group input[type=range] { flex:1; accent-color:var(--accent); }
.slider-group .val { font-size:13px; color:var(--accent); min-width:36px; text-align:right; }

.stat-row { display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px solid rgba(255,255,255,0.03); font-size:13px; }
.stat-row .label { color:var(--text2); }
.stat-row .value { font-weight:600; }
.stat-row .value.hat { color:var(--accent2); }
.stat-row .value.person { color:#4da6ff; }

.det-item { display:flex; align-items:center; gap:8px; padding:6px 0; font-size:12px; }
.det-item .dot { width:8px; height:8px; border-radius:50%; flex-shrink:0; }
.det-item .dot.hat { background:var(--accent2); }
.det-item .dot.person { background:#4da6ff; }
.det-item .conf { margin-left:auto; color:var(--text2); font-family:monospace; }

.upload-zone { border:2px dashed rgba(255,255,255,0.15); border-radius:var(--radius); padding:40px 20px; text-align:center; cursor:pointer; transition:all .3s; color:var(--text2); }
.upload-zone:hover, .upload-zone.drag { border-color:var(--accent); background:rgba(0,212,255,0.05); color:var(--accent); }
.upload-zone .icon { font-size:36px; margin-bottom:8px; display:block; }
.upload-zone input { display:none; }

.status-bar { padding:8px 24px; background:#0a0a14; border-top:1px solid rgba(255,255,255,0.05); font-size:12px; color:var(--text2); display:flex; gap:16px; }
.status-bar .live { color:var(--accent2); }
.status-bar .live::before { content:"● "; animation:pulse 1.5s infinite; }
@keyframes pulse { 50%{opacity:0.3;} }

@media (max-width:768px) { .sidebar { width:100%; position:absolute; right:0; top:56px; bottom:32px; display:none; } }
</style>
</head>
<body>

<div class="header">
  <h1>ODPlatform</h1>
  <span class="badge">安全帽检测</span>
  <span class="device-badge" id="deviceBadge">加载中...</span>
</div>

<div class="main">
  <div class="display" id="display">
    <div class="placeholder">
      <div class="icon">&#x1f6e0;</div>
      <div>选择模式开始推理</div>
    </div>
  </div>

  <div class="sidebar">
    <section>
      <h3>模式</h3>
      <div class="mode-group">
        <button class="mode-btn active" data-mode="webcam">实时摄像头</button>
        <button class="mode-btn" data-mode="video">视频文件</button>
        <button class="mode-btn" data-mode="image">图片上传</button>
      </div>
    </section>

    <section id="webcamControls">
      <button class="btn btn-start" id="btnWebcam" onclick="toggleWebcam()">启动摄像头</button>
    </section>

    <section id="videoControls" style="display:none;">
      <button class="btn btn-start" id="btnVideo" onclick="toggleVideo()">选择视频文件</button>
      <input type="file" id="videoFileInput" accept="video/mp4,video/avi,video/mov,video/webm" style="display:none;">
    </section>

    <section id="imageControls" style="display:none;">
      <div class="upload-zone" id="uploadZone">
        <span class="icon">&#128196;</span>
        <span>拖拽图片到此处 或 点击选择文件</span>
        <input type="file" id="fileInput" accept="image/jpeg,image/png,image/bmp">
      </div>
    </section>

    <section>
      <h3>置信度阈值</h3>
      <div class="slider-group">
        <input type="range" min="0.1" max="0.9" step="0.05" value="0.25" id="confSlider" oninput="updateConf()">
        <span class="val" id="confVal">0.25</span>
      </div>
    </section>

    <section>
      <h3>检测统计</h3>
      <div id="stats">
        <div class="stat-row"><span class="label">FPS</span><span class="value" id="statFps">—</span></div>
        <div class="stat-row"><span class="label">推理耗时</span><span class="value" id="statInfer">—</span></div>
        <div class="stat-row"><span class="label">安全帽 (hat)</span><span class="value hat" id="statHat">—</span></div>
        <div class="stat-row"><span class="label">人员 (person)</span><span class="value person" id="statPerson">—</span></div>
      </div>
    </section>

    <section>
      <h3>检测列表</h3>
      <div id="detList" style="max-height:200px;overflow-y:auto;"></div>
    </section>
  </div>
</div>

<div class="status-bar">
  <span id="statusText">就绪</span>
  <span id="statusModel" style="margin-left:auto;">模型: 加载中...</span>
</div>

<script>
let mode = "webcam";
let ws = null;
let stream = null;
let videoEl = null;
let canvasEl = null;
let animId = null;
let wsReady = false;

document.querySelectorAll(".mode-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    if (ws) { ws.close(); ws = null; }
    if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
    if (animId) cancelAnimationFrame(animId);
    mode = btn.dataset.mode;
    document.querySelectorAll(".mode-btn").forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById("webcamControls").style.display = mode === "webcam" ? "" : "none";
    document.getElementById("videoControls").style.display = mode === "video" ? "" : "none";
    document.getElementById("imageControls").style.display = mode === "image" ? "" : "none";
    document.getElementById("display").innerHTML = '<div class="placeholder"><div class="icon">&#x1f6e0;</div><div>选择模式开始推理</div></div>';
    clearStats();
    setStatus("就绪");
    document.getElementById("btnWebcam").textContent = "启动摄像头";
    document.getElementById("btnWebcam").className = "btn btn-start";
    document.getElementById("btnVideo").textContent = "选择视频文件";
    document.getElementById("btnVideo").className = "btn btn-start";
  });
});

async function toggleWebcam() {
  if (ws) { stopWebcam(); return; }
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
    videoEl = document.createElement("video");
    videoEl.srcObject = stream;
    videoEl.playsInline = true;
    await videoEl.play();
    canvasEl = document.createElement("canvas");
    canvasEl.width = 640;
    canvasEl.height = 480;
    connectWebSocket();
    document.getElementById("btnWebcam").textContent = "停止";
    document.getElementById("btnWebcam").className = "btn btn-stop";
    setStatus("摄像头运行中", true);
    scheduleFrame();
  } catch (e) {
    setStatus("摄像头失败: " + e.message);
  }
}

function stopWebcam() {
  if (ws) { ws.close(); ws = null; wsReady = false; }
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }
  if (animId) { cancelAnimationFrame(animId); animId = null; }
  videoEl = null;
  document.getElementById("btnWebcam").textContent = "启动摄像头";
  document.getElementById("btnWebcam").className = "btn btn-start";
  document.getElementById("btnVideo").textContent = "选择视频文件";
  document.getElementById("btnVideo").className = "btn btn-start";
  setStatus("已停止");
}

async function toggleVideo() {
  if (ws) { stopWebcam(); return; }
  const input = document.getElementById("videoFileInput");
  input.onchange = async () => {
    if (!input.files.length) return;
    const file = input.files[0];
    videoEl = document.createElement("video");
    videoEl.src = URL.createObjectURL(file);
    videoEl.playsInline = true;
    videoEl.loop = true;
    videoEl.muted = true;
    await videoEl.play();
    canvasEl = document.createElement("canvas");
    canvasEl.width = 640;
    canvasEl.height = Math.round(videoEl.videoHeight / videoEl.videoWidth * 640) || 480;
    connectWebSocket();
    document.getElementById("btnVideo").textContent = "停止";
    document.getElementById("btnVideo").className = "btn btn-stop";
    setStatus("视频推理中", true);
    scheduleFrame();
  };
  input.click();
}

function scheduleFrame() {
  animId = requestAnimationFrame(() => {
    if (!videoEl || !ws || !wsReady || ws.readyState !== WebSocket.OPEN) {
      scheduleFrame(); return;
    }
    const ctx = canvasEl.getContext("2d");
    const vw = videoEl.videoWidth || 640, vh = videoEl.videoHeight || 480;
    const scale = Math.min(640 / vw, 480 / vh);
    const dw = vw * scale, dh = vh * scale;
    canvasEl.width = dw; canvasEl.height = dh;
    ctx.drawImage(videoEl, 0, 0, dw, dh);
    canvasEl.toBlob(blob => {
      if (blob && ws && ws.readyState === WebSocket.OPEN) {
        ws.send(blob);
      }
      scheduleFrame();
    }, "image/jpeg", 0.72);
  });
}

function connectWebSocket() {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  ws = new WebSocket(proto + "://" + location.host + "/ws/realtime");
  ws.binaryType = "arraybuffer";
  ws.onopen = () => {
    ws.send(JSON.stringify({ conf: parseFloat(document.getElementById("confSlider").value) }));
  };
  ws.onmessage = (e) => {
    const data = JSON.parse(e.data);
    if (data.error) { setStatus("错误: " + data.error); return; }
    if (data.status === "ready") {
      wsReady = true;
      document.getElementById("deviceBadge").textContent = data.device === "0" ? "GPU" : "CPU";
      document.getElementById("statusModel").textContent = "模型: " + data.classes.join(", ");
      return;
    }
    updateDisplay(data);
  };
  ws.onclose = () => { wsReady = false; };
}

async function uploadImage(file) {
  setStatus("推理中...");
  const form = new FormData();
  form.append("file", file);
  form.append("conf", document.getElementById("confSlider").value);
  try {
    const res = await fetch("/infer/image", { method: "POST", body: form });
    const data = await res.json();
    if (data.success) {
      updateDisplay(data);
      setStatus("推理完成 (" + data.inference_time_ms + "ms)");
    } else {
      setStatus("错误: " + data.error);
    }
  } catch (e) {
    setStatus("请求失败: " + e.message);
  }
}

function updateDisplay(data) {
  const disp = document.getElementById("display");
  if (data.image) {
    disp.innerHTML = '<img src="' + data.image + '" alt="detection">';
  }
  document.getElementById("statFps").textContent = data.fps ? data.fps.toFixed(1) : "—";
  document.getElementById("statInfer").textContent = data.inference_time_ms ? data.inference_time_ms + " ms" : "—";
  document.getElementById("statHat").textContent = (data.counts && data.counts.hat) || 0;
  document.getElementById("statPerson").textContent = (data.counts && data.counts.person) || 0;

  const list = document.getElementById("detList");
  if (data.detections && data.detections.length) {
    list.innerHTML = data.detections.map(d =>
      '<div class="det-item"><span class="dot ' + d.class_name + '"></span>' +
      d.class_name + ' <span class="conf">' + (d.confidence * 100).toFixed(1) + '%</span></div>'
    ).join("");
  } else {
    list.innerHTML = '<div style="color:var(--text2);font-size:12px;">未检测到目标</div>';
  }
}

function clearStats() {
  ["statFps","statInfer","statHat","statPerson"].forEach(id => document.getElementById(id).textContent = "—");
  document.getElementById("detList").innerHTML = "";
}

function setStatus(msg, live) {
  const el = document.getElementById("statusText");
  el.textContent = msg;
  el.className = live ? "live" : "";
}

function updateConf() {
  const v = document.getElementById("confSlider").value;
  document.getElementById("confVal").textContent = v;
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ conf: parseFloat(v) }));
  }
}

const uploadZone = document.getElementById("uploadZone");
const fileInput = document.getElementById("fileInput");
uploadZone.addEventListener("click", () => fileInput.click());
uploadZone.addEventListener("dragover", e => { e.preventDefault(); uploadZone.classList.add("drag"); });
uploadZone.addEventListener("dragleave", () => uploadZone.classList.remove("drag"));
uploadZone.addEventListener("drop", e => {
  e.preventDefault(); uploadZone.classList.remove("drag");
  if (e.dataTransfer.files.length) uploadImage(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) uploadImage(fileInput.files[0]);
});

(async () => {
  try { await fetch("/"); } catch(e) {}
  document.getElementById("deviceBadge").textContent = "Web";
  document.getElementById("statusModel").textContent = "模型: exp_20260614_125153_best.pt";
  setStatus("就绪");
})();
</script>
</body>
</html>"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
