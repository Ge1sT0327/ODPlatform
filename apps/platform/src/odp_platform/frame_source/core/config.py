"""摄像头配置。"""

from enum import Enum
from pydantic import BaseModel, Field

class CameraBackend(str, Enum):
    ANY = "any"
    MSMF = "msmf"        # Windows
    DSHOW = "dshow"      # Windows DirectShow
    V4L2 = "v4l2"        # Linux
    AVFOUNDATION = "avfoundation"  # macOS

class CameraCodec(str, Enum):
    MJPG = "MJPG"
    YUY2 = "YUY2"
    H264 = "H264"

class CameraConfig(BaseModel):
    """摄像头配置。set() 请求参数，get() 读回实测值。"""
    width: int = Field(default=1280, description="请求分辨率宽度")
    height: int = Field(default=720, description="请求分辨率高度")
    fps: int = Field(default=30, description="请求帧率")
    backend: CameraBackend = Field(default=CameraBackend.ANY, description="采集后端")
    codec: CameraCodec = Field(default=CameraCodec.MJPG, description="编码格式")
    auto_exposure: float = Field(default=-1, description="自动曝光（-1=不设置）")
    brightness: int = Field(default=-1, description="亮度（-1=不设置）")
