# TensorRT Deployment Guide

## Status: ONNX ready, TRT pending SDK

- ONNX export: SUCCESS (11.7 MB)
- TRT engine: requires NVIDIA TensorRT SDK on Windows
  - Looking in indexes: https://mirrors.aliyun.com/pypi/simple/
Requirement already satisfied: tensorrt in d:naconda\lib\site-packages (11.0.0.114)
Requirement already satisfied: tensorrt_cu13==11.0.0.114 in d:naconda\lib\site-packages (from tensorrt) (11.0.0.114)
Requirement already satisfied: tensorrt_cu13_libs==11.0.0.114 in d:naconda\lib\site-packages (from tensorrt_cu13==11.0.0.114->tensorrt) (11.0.0.114)
Requirement already satisfied: tensorrt_cu13_bindings==11.0.0.114 in d:naconda\lib\site-packages (from tensorrt_cu13==11.0.0.114->tensorrt) (11.0.0.114) (from NVIDIA index)
  - Or download TensorRT ZIP from NVIDIA Developer

## Export Steps

WARNING GitHub assets check failure for https://api.github.com/repos/ultralytics/assets/releases/tags/v8.4.0: 403 rate limit exceeded
WARNING GitHub assets check failure for https://api.github.com/repos/ultralytics/assets/releases/latest: 403 rate limit exceeded

## Real Performance Benchmarks (RTX 3070, batch=1, 640x640)

| Format | Avg Latency | Speedup vs PT | File Size |
|--------|------------|---------------|-----------|
| PyTorch (.pt) | 11.9ms | 1.0x | 6.0 MB |
| ONNX (.onnx) | 6.9ms | 1.7x | 11.7 MB |
| TensorRT (.engine) | ~2.7ms* | ~4.4x | ~12 MB |

> *Estimated: ONNX->TRT typically yields 2-3x over ONNX inference.
> Loop FPS (with camera overhead): PT ~75-78 -> TRT ~80-85 -> approaching 90 FPS camera cap.

## Using Engine in Pipeline

WARNING GitHub assets check failure for https://api.github.com/repos/ultralytics/assets/releases/tags/v8.4.0: 403 rate limit exceeded
WARNING GitHub assets check failure for https://api.github.com/repos/ultralytics/assets/releases/latest: 403 rate limit exceeded

## Requirements
- NVIDIA GPU (Ampere+: RTX 30xx+)
- CUDA 11.8+ / 12.x
- TensorRT SDK (Windows: download from NVIDIA Developer)
- Looking in indexes: https://mirrors.aliyun.com/pypi/simple/, https://pypi.nvidia.com
Requirement already satisfied: tensorrt in d:naconda\lib\site-packages (11.0.0.114)
Requirement already satisfied: tensorrt_cu13==11.0.0.114 in d:naconda\lib\site-packages (from tensorrt) (11.0.0.114)
Requirement already satisfied: tensorrt_cu13_libs==11.0.0.114 in d:naconda\lib\site-packages (from tensorrt_cu13==11.0.0.114->tensorrt) (11.0.0.114)
Requirement already satisfied: tensorrt_cu13_bindings==11.0.0.114 in d:naconda\lib\site-packages (from tensorrt_cu13==11.0.0.114->tensorrt) (11.0.0.114)
