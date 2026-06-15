# frame_source — 统一帧源模块

## 是什么

为"图/视频/目录/摄像头/RTSP"提供统一的出帧抽象。
设计目标：零宿主依赖，整包拷至任意 Python 项目即可用。

## 依赖

- opencv-python >= 4.8.0
- pydantic >= 2.0.0 (仅 CameraConfig)
- numpy >= 1.24.0

## 快速开始

