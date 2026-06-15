"""核心数据类型。"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import numpy as np

class SourceType(str, Enum):
    IMAGE = "image"
    IMAGE_FOLDER = "image_folder"
    VIDEO = "video"
    CAMERA = "camera"
    RTSP = "rtsp"

@dataclass(frozen=True)
class FrameInfo:
    """帧元数据（不可变）。"""
    frame_index: int = 0           # 从 0 开始的帧序号
    timestamp: float = 0.0         # 相对时间戳（秒）
    source_type: SourceType = SourceType.IMAGE
    original_width: int = 0
    original_height: int = 0
    fps: float = 0.0               # 帧源标称帧率

@dataclass
class Frame:
    """单帧数据。image 为 BGR ndarray。"""
    image: "np.ndarray"
    info: FrameInfo = field(default_factory=FrameInfo)

    @property
    def width(self) -> int:
        return self.image.shape[1] if self.image is not None else 0

    @property
    def height(self) -> int:
        return self.image.shape[0] if self.image is not None else 0
