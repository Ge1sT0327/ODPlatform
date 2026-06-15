"""frame_source — 统一帧源抽象（零宿主依赖，可整包移植）。"""

# 自带扩展名常量必须在最前定义/导出，避免子模块循环导入
from odp_platform.frame_source.constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from odp_platform.frame_source.core.types import Frame, FrameInfo, SourceType
from odp_platform.frame_source.core.config import CameraConfig, CameraBackend, CameraCodec
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.factory import create_frame_source
from odp_platform.frame_source.sources.image import ImageSource, ImageFolderSource
from odp_platform.frame_source.sources.video import VideoSource
from odp_platform.frame_source.sources.camera import CameraSource
from odp_platform.frame_source.wrappers.threaded import ThreadedSource, create_threaded_source
from odp_platform.frame_source.wrappers.aio import AsyncSource

__all__ = [
    "create_frame_source", "FrameSource",
    "Frame", "FrameInfo", "SourceType",
    "CameraConfig", "CameraBackend", "CameraCodec",
    "ImageSource", "ImageFolderSource", "VideoSource", "CameraSource",
    "ThreadedSource", "AsyncSource", "create_threaded_source",
    "IMAGE_EXTENSIONS", "VIDEO_EXTENSIONS",
]
