"""摄像头源：参数协商 + 后端协商 + 实测回读 + 高帧率支持。

撞墙记录 (来自雨霓同学):
    1. MSMF 后端必须在 cv2.VideoCapture 创建之前设置环境变量
       OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS=0, 否则帧率下降 20-30%
    2. 参数设置顺序必须是: 分辨率 -> FOURCC -> FPS,
       否则 MSMF 下高帧率请求会被驱动重新协商时覆盖, 完全失效
    3. set() 是请求不是命令, 必须 read 一帧触发驱动协商, 再 get 读回真实值
"""

import logging
import os
import time
from typing import Optional

import cv2
import numpy as np

from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.core.types import Frame, FrameInfo, SourceType
from odp_platform.frame_source.core.config import CameraConfig

logger = logging.getLogger(__name__)

_BACKEND_MAP = {
    "any": cv2.CAP_ANY,
    "msmf": cv2.CAP_MSMF,
    "dshow": cv2.CAP_DSHOW,
    "v4l2": cv2.CAP_V4L2,
}


class CameraSource(FrameSource):
    """摄像头输入源, 支持指定分辨率/帧率/后端/编码。

    示例:
        # 默认 (1280x720 @ 30fps)
        with CameraSource(0) as cam:
            for frame in cam:
                process(frame.image)

        # 高帧率 (Windows: MSMF + MJPG)
        config = CameraConfig(width=1280, height=720, fps=90, backend="msmf")
        with CameraSource(0, config) as cam:
            for frame in cam:
                process(frame.image)
    """

    def __init__(self, device: int | str = 0, config: CameraConfig = None):
        super().__init__()
        self.device = int(device) if str(device).isdigit() else device
        self.config = config or CameraConfig()
        self._cap: Optional[cv2.VideoCapture] = None
        self._actual_width: int = 0
        self._actual_height: int = 0
        self._actual_fps: float = 0.0
        self._start_time: float = 0.0
        self._frame_index: int = 0

    @property
    def source_type(self) -> SourceType:
        return SourceType.CAMERA if isinstance(self.device, int) else SourceType.RTSP

    def _open(self) -> bool:
        # 【撞墙记录 1】MSMF 必须在 VideoCapture 创建前设环境变量
        # 关闭 MSMF 自动插入的硬件色彩转换滤镜, 否则帧率下降 20-30%
        if self.config.backend == "msmf":
            os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"

        backend = _BACKEND_MAP.get(self.config.backend, cv2.CAP_ANY)
        self._cap = cv2.VideoCapture(self.device, backend)
        if not self._cap.isOpened():
            logger.error(f"无法打开摄像头 {self.device}")
            return False

        # 【撞墙记录 2】参数设置顺序: 分辨率 -> FOURCC -> FPS (不能改!)
        # 1. 先设分辨率: 驱动据此筛选可用的媒体类型列表
        # 2. 再设 FOURCC: 从上一步的列表中选择编码格式 (MJPG)
        # 3. 最后设 FPS: 格式锁定后才约束帧率
        self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
        self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
        codec_int = cv2.VideoWriter_fourcc(*self.config.codec)
        self._cap.set(cv2.CAP_PROP_FOURCC, codec_int)
        self._cap.set(cv2.CAP_PROP_FPS, self.config.fps)

        # 【撞墙记录 3】set() 只是登记意图, 必须 read 一帧触发硬件协商
        # 没有这次 read(), get() 返回的是"请求值"而非"实际值"
        ret, _ = self._cap.read()
        if not ret:
            logger.warning("格式协商触发帧读取失败, 实际参数可能不准确")

        # 读回实际生效的参数
        self._actual_width = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._actual_height = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._actual_fps = self._cap.get(cv2.CAP_PROP_FPS)

        # 验证：期望 vs 实际
        if self._actual_width != self.config.width or self._actual_height != self.config.height:
            logger.warning(
                f"分辨率未完全生效: 期望 {self.config.width}x{self.config.height}, "
                f"实际 {self._actual_width}x{self._actual_height}"
            )
        if self._actual_fps < self.config.fps * 0.9:
            logger.warning(
                f"帧率未完全生效: 期望 {self.config.fps}fps, "
                f"实际标称 {self._actual_fps:.1f}fps"
            )

        self._start_time = time.time()
        logger.info(
            f"摄像头已打开 (backend={self.config.backend}, codec={self.config.codec})"
        )
        logger.info(
            f"  目标: {self.config.width}x{self.config.height} @ {self.config.fps}fps"
        )
        logger.info(
            f"  实际: {self._actual_width}x{self._actual_height} @ {self._actual_fps:.1f}fps"
        )
        return True

    def _read(self) -> Optional[Frame]:
        if self._cap is None:
            return None
        ret, img = self._cap.read()
        if not ret:
            return None

        info = FrameInfo(
            original_width=self._actual_width,
            original_height=self._actual_height,
            source_type=self.source_type,
            timestamp=time.time() - self._start_time,
            frame_index=self._frame_index,
            fps=self._actual_fps,
        )
        self._frame_index += 1
        return Frame(image=img, info=info)

    def _close(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
            logger.info("摄像头已关闭")

    @property
    def actual_width(self) -> int:
        return self._actual_width

    @property
    def actual_height(self) -> int:
        return self._actual_height

    @property
    def actual_fps(self) -> float:
        return self._actual_fps
