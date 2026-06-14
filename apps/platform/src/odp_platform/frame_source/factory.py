"""create_frame_source：字符串自动识别 + fail-fast。"""

from pathlib import Path
from typing import Union
from odp_platform.frame_source.core.config import CameraConfig
from odp_platform.frame_source.core.base import FrameSource
from odp_platform.frame_source.constants import IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from odp_platform.frame_source.sources.image import ImageSource, ImageFolderSource
from odp_platform.frame_source.sources.video import VideoSource
from odp_platform.frame_source.sources.camera import CameraSource

def create_frame_source(
    source: Union[str, int],
    camera_config: CameraConfig = None,
) -> FrameSource:
    """
    根据 source 字符串自动识别源类型:

    - "0", "1" ... → CameraSource (摄像头)
    - "rtsp://..."  → CameraSource (RTSP)
    - 存在的图片文件  → ImageSource
    - 存在的目录     → ImageFolderSource
    - 存在的视频文件  → VideoSource
    - 路径不存在     → raise ValueError

    摄像头参数可通过 camera_config 显式配置（分辨率/帧率/后端/编码）。
    """
    if isinstance(source, int):
        return CameraSource(source, camera_config)

    s = str(source)

    # RTSP/HTTP 流
    if s.startswith("rtsp://") or s.startswith("http://"):
        return CameraSource(s, camera_config)

    # 数字字符串 → 摄像头
    if s.isdigit():
        return CameraSource(int(s), camera_config)

    # 文件/目录
    p = Path(s)
    if not p.exists():
        raise ValueError(f"帧源路径不存在: '{s}'。支持: 摄像头序号、图片路径、目录路径、视频路径、RTSP URL。")

    if p.is_file():
        ext = p.suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            return ImageSource(p)
        if ext in VIDEO_EXTENSIONS:
            return VideoSource(p)
        raise ValueError(f"不支持的文件格式: '{ext}'。支持的图片: {IMAGE_EXTENSIONS}，视频: {VIDEO_EXTENSIONS}")

    if p.is_dir():
        return ImageFolderSource(p)

    raise ValueError(f"无法识别的帧源: '{s}'")
