"""多线程推理流水线：采集→推理→输出。通过 Queue 解耦。"""

import time
import threading
import queue as qmod
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path
from abc import ABC, abstractmethod

from odp_platform.frame_source.core.types import Frame
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.common.logging_utils import get_logger
from odp_platform.common.model_utils import resolve_model_path

class CancelToken:
    """取消信号。"""
    def __init__(self):
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

class InferHooks:
    """生命周期回调。"""
    def on_start(self) -> None: pass
    def on_frame(self, frame: Frame, detections: list) -> None: pass
    def on_stop(self, result: "InferResult") -> None: pass

class OutputSink(ABC):
    """输出接缝。推理引擎不依赖任何前端框架。"""
    @abstractmethod
    def consume(self, frame: Frame, detections: list) -> None: ...
    @abstractmethod
    def close(self) -> None: ...

@dataclass
class InferResult:
    success: bool = True
    error: Optional[str] = None
    frames_processed: int = 0
    total_time: float = 0.0
    fps: float = 0.0

class InferService:
    """
    三线程流水线：
      Thread 1: 采集 (frame_source)
      Thread 2: 推理 (model)
      Thread 3: 输出 (sink)
    通过 Queue 解耦，CancelToken 控制优雅退出。
    """

    def __init__(
        self,
        source: FrameSource,
        model_path: str | Path,
        sink: OutputSink,
        hooks: InferHooks = None,
        cancel: CancelToken = None,
        conf: float = 0.25,
        iou: float = 0.7,
        imgsz: int = 640,
        device: str = "auto",
    ):
        self.source = source
        self.model_path = model_path
        self.sink = sink
        self.hooks = hooks or InferHooks()
        self.cancel = cancel or CancelToken()
        self.conf = conf
        self.iou = iou
        self.imgsz = imgsz
        self.device = device
        self.logger = get_logger("inference", log_type="infer")

        self._frame_queue = qmod.Queue(maxsize=16)
        self._result_queue = qmod.Queue(maxsize=16)

    def run(self) -> InferResult:
        """启动三线程流水线，阻塞直到结束或取消。"""
        from ultralytics import YOLO
        model_path = resolve_model_path(str(self.model_path))
        model = YOLO(str(model_path))

        self.hooks.on_start()
        t0 = time.perf_counter()
        self.cancel._event.clear()

        # Thread 1: 采集
        def collector():
            try:
                with self.source as src:
                    for frame in src:
                        if self.cancel.is_cancelled:
                            break
                        self._frame_queue.put(frame)
            except Exception as e:
                self.logger.error(f"采集异常: {e}")
            finally:
                self._frame_queue.put(None)  # 采集结束哨兵

        # Thread 2: 推理
        def predictor():
            while not self.cancel.is_cancelled:
                try:
                    frame = self._frame_queue.get(timeout=0.5)
                except qmod.Empty:
                    continue
                if frame is None:  # 哨兵
                    self._result_queue.put(None)
                    break
                results = model(frame.image, conf=self.conf, iou=self.iou,
                               imgsz=self.imgsz, device=self.device, verbose=False)
                dets = []
                if results and results[0].boxes:
                    for box in results[0].boxes:
                        dets.append({
                            "bbox": box.xyxy[0].tolist(),
                            "confidence": float(box.conf[0]),
                            "class_id": int(box.cls[0]),
                            "class_name": model.names.get(int(box.cls[0]), str(int(box.cls[0]))),
                        })
                self._result_queue.put((frame, dets))

        # Thread 3: 输出
        frames_processed = 0
        def consumer():
            nonlocal frames_processed
            while not self.cancel.is_cancelled:
                try:
                    item = self._result_queue.get(timeout=0.5)
                except qmod.Empty:
                    continue
                if item is None:
                    break
                frame, dets = item
                self.hooks.on_frame(frame, dets)
                self.sink.consume(frame, dets)
                frames_processed += 1
            self.sink.close()

        t_collect = threading.Thread(target=collector, daemon=True)
        t_predict = threading.Thread(target=predictor, daemon=True)
        t_consume = threading.Thread(target=consumer, daemon=True)

        for t in [t_collect, t_predict, t_consume]:
            t.start()
        for t in [t_collect, t_predict, t_consume]:
            t.join(timeout=30)

        elapsed = time.perf_counter() - t0
        fps = frames_processed / elapsed if elapsed > 0 else 0
        result = InferResult(success=True, frames_processed=frames_processed,
                            total_time=elapsed, fps=fps)
        self.hooks.on_stop(result)
        return result

def infer_yolo(
    source: str | int,
    model_path: str = "yolov8n.pt",
    sink: OutputSink = None,
    conf: float = 0.25,
    **kwargs,
) -> InferResult:
    """便捷推理函数。"""
    from odp_platform.frame_source.factory import create_frame_source
    from odp_platform.inference.sinks import DisplaySink, NoopSink
    # 根据参数选择默认 sink；show 只用于选择 sink，不传给 InferService
    if sink is None:
        if kwargs.pop("show", False):
            sink = DisplaySink()
        else:
            sink = NoopSink()
    fs = create_frame_source(source)
    service = InferService(source=fs, model_path=model_path, sink=sink, conf=conf, **kwargs)
    return service.run()
