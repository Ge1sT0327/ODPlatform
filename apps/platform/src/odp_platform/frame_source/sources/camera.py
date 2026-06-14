"""摄像头源：参数协商 + 后端协商 + 实测回读。"""

from typing import Optional
import cv2
import numpy as np
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.core.types import Frame, FrameInfo, SourceType
from odp_platform.frame_source.core.config import CameraConfig, CameraBackend

# backend 字符串映射（跨平台）
_BACKEND_MAP = {
    CameraBackend.MSMF: cv2.CAP_MSMF,
    CameraBackend.DSHOW: cv2.CAP_DSHOW,
    CameraBackend.V4L2: cv2.CAP_V4L2,
    CameraBackend.AVFOUNDATION: cv2.CAP_AVFOUNDATION,
    CameraBackend.ANY: cv2.CAP_ANY,
}

class CameraSource(FrameSource):
    def __init__(self, device: int | str = 0, config: CameraConfig = None):
        super().__init__()
        self.device = int(device) if str(device).isdigit() else device
        self.config = config or CameraConfig()
        self._cap: Optional[cv2.VideoCapture] = None
        self._actual_width: int = 0
        self._actual_height: int = 0
        self._actual_fps: float = 0.0

    @property
    def source_type(self) -> SourceType:
        return SourceType.CAMERA if isinstance(self.device, int) else SourceType.RTSP

    def _open(self) -> bool:
        backend = _BACKEND_MAP.get(self.config.backend, cv2.CAP_ANY)
        self._cap = cv2.VideoCapture(self.device, backend)
        if not self._cap.isOpened():
            return False

        # 参数协商：set() 请求 + get() 读回实测
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        self._cap.set(cv2.CAP_PROP_FPS, self.config.fps)
        if self.config.codec:
            codec_int = cv2.VideoWriter_fourcc(*self.config.codec.value)
            self._cap.set(cv2.CAP_PROP_FOURCC, codec_int)

        # 读回实测值（非标称！）
        self._actual_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._actual_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._actual_fps = self._cap.get(cv2.CAP_PROP_FPS)
        return True

    def _read(self) -> Optional[Frame]:
        if self._cap is None:
            return None
        ret, img = self._cap.read()
        if not ret:
            return None
        return Frame(
            image=img,
            info=FrameInfo(
                original_width=self._actual_width,
                original_height=self._actual_height,
                timestamp=cv2.getTickCount() / cv2.getTickFrequency(),
                source_type=self.source_type,
            ),
        )

    def _close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None

    @property
    def actual_width(self) -> int:
        return self._actual_width

    @property
    def actual_height(self) -> int:
        return self._actual_height

    @property
    def actual_fps(self) -> float:
        return self._actual_fps
