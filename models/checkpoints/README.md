# Model Weights

## yolov8n_safety_helmet_best.pt
- Base: YOLOv8n (Ultralytics, 3.0M params, 8.1 GFLOPs)
- Pretrained: yolov8n.pt (COCO, official release)
- Dataset: SHWD safety helmet (7581 imgs, 2 classes: hat/person)
- GPU: NVIDIA RTX 4090 (24GB), CUDA 12.1
- Config: epochs=100, batch=16, imgsz=640
- Result: mAP50=0.939, mAP50-95=0.616
- Size: 6.0 MB
- Date: 2025-06-14
