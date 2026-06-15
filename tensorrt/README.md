# TensorRT Deployment Guide

## Export Engine

```bash
yolo export model=models/checkpoints/yolov8n_safety_helmet_best.pt format=engine imgsz=640 batch=1 device=0
yolo export model=models/checkpoints/yolov8n_safety_helmet_best.pt format=engine imgsz=640 batch=1 half=True device=0  # FP16
```

## Inference (zero code change)

```bash
odp-infer --source 0 --model yolov8n_safety_helmet_best.engine --imgsz 640
python apps/web-backend/server.py  # select .engine as model
```

## Performance (RTX 3070)

| Format | Infer Time | Loop FPS |
|--------|-----------|----------|
| .pt (PyTorch) | ~10ms | ~75-78 |
| .engine (TRT FP32) | ~5ms | ~80-85 |
| .engine (TRT FP16) | ~4ms | ~85-90 |

> Bind GPU+TRT version. Rebuild on target. Raw trtexec engine: `scripts/wrap_trt_engine.py`.
