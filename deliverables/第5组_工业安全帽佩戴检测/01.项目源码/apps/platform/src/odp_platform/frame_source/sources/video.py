"""视频源：视频文件 → 逐帧迭代 + seek。"""

from pathlib import Path
from typing import Optional
import cv2
import numpy as np
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.core.types import Frame, FrameInfo, SourceType

class VideoSource(FrameSource):
    def __init__(self, path: str | Path):
        super().__init__()
        self.path = Path(path)
        self._cap: Optional[cv2.VideoCapture] = None
        self._fps: float = 0.0
        self._total_frames: int = 0

    @property
    def source_type(self) -> SourceType:
        return SourceType.VIDEO

    def _open(self) -> bool:
        if not self.path.exists():
            raise ValueError(f"视频文件不存在: {self.path}")
        self._cap = cv2.VideoCapture(str(self.path))
        if not self._cap.isOpened():
            return False
        self._fps = self._cap.get(cv2.CAP_PROP_FPS)
        self._total_frames = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return True

    def _read(self) -> Optional[Frame]:
        if self._cap is None:
            return None
        ret, img = self._cap.read()
        if not ret:
            return None
        h, w = img.shape[:2]
        pos_msec = self._cap.get(cv2.CAP_PROP_POS_MSEC)
        return Frame(
            image=img,
            info=FrameInfo(
                original_width=w, original_height=h,
                timestamp=pos_msec / 1000.0, source_type=SourceType.VIDEO,
            ),
        )

    def _close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    def seek(self, frame_idx: int = None, time_sec: float = None) -> None:
        """跳转到指定帧号或时间（秒）。"""
        if self._cap is None:
            return
        if frame_idx is not None:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        elif time_sec is not None:
            self._cap.set(cv2.CAP_PROP_POS_MSEC, time_sec * 1000)

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def total_frames(self) -> int:
        return self._total_frames
