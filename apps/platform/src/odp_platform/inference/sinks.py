"""内置 OutputSink 实现 (兼容新旧接口)。"""

import cv2
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


# ── 新版 OutputSink (teacher 接口: open/write/close) ───────
class OutputSink(ABC):
    """输出接缝。"""
    @abstractmethod
    def open(self, output_dir, source_type) -> None: ...
    @abstractmethod
    def write(self, frame, annotated) -> None: ...
    @abstractmethod
    def close(self) -> None: ...


class NullSink(OutputSink):
    """空输出 — 纯推理基准。"""
    def open(self, output_dir, source_type) -> None: pass
    def write(self, frame, annotated) -> None: pass
    def close(self) -> None: pass


class LocalFileSink(OutputSink):
    """保存推理结果到本地文件。"""
    def __init__(self):
        self._output_dir: Optional[Path] = None
        self._img_dir: Optional[Path] = None
        self._counter: int = 0

    def open(self, output_dir, source_type) -> None:
        self._output_dir = Path(output_dir)
        self._img_dir = self._output_dir / "images"
        self._img_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def write(self, frame, annotated) -> None:
        if self._img_dir is None:
            return
        fname = self._img_dir / f"frame_{self._counter:06d}.jpg"
        cv2.imwrite(str(fname), annotated)
        self._counter += 1

    def close(self) -> None:
        if self._counter:
            logger.info(f"LocalFileSink: saved {self._counter} frames to {self._output_dir}")


# ── 旧版 Sink (consume 接口, 向后兼容桌面GUI) ──────────────
class DisplaySink:
    """cv2.imshow 实时显示。"""
    def __init__(self, window_name: str = "ODPlatform Inference"):
        self.window_name = window_name
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def consume(self, frame, detections: list) -> None:
        cv2.imshow(self.window_name, frame.image)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            raise KeyboardInterrupt("用户按 q 退出")
        if key == ord(" "):
            cv2.waitKey(0)

    def close(self) -> None:
        cv2.destroyWindow(self.window_name)


class SaveVideoSink:
    """保存输出为视频文件。"""
    def __init__(self, output_path: str = None, fps: float = 30.0):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_path = Path(output_path or f"output_{ts}.mp4")
        self.fps = fps
        self._writer = None

    def consume(self, frame, detections: list) -> None:
        if self._writer is None:
            h, w = frame.image.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self._writer = cv2.VideoWriter(str(self.output_path), fourcc, self.fps, (w, h))
        self._writer.write(frame.image)

    def close(self) -> None:
        if self._writer is not None:
            self._writer.release()


class NoopSink:
    """不做任何输出（旧版兼容）。"""
    def consume(self, frame, detections: list) -> None:
        pass

    def close(self) -> None:
        pass
