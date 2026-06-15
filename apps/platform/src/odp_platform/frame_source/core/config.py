"""摄像头配置 (Pydantic v2)。"""

from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

CameraBackend = Literal["any", "msmf", "dshow", "v4l2"]
CameraCodec = Literal["MJPG", "YUYV", "H264", "MP4V"]

class CameraConfig(BaseModel):
    """摄像头配置。set() 请求参数，get() 读回实测值。

    示例:
        # 默认 (1280x720 @ 30fps)
        config = CameraConfig()

        # 高帧率 (Windows: MSMF 后端 + MJPG 编码)
        config = CameraConfig(width=1280, height=720, fps=90, backend="msmf")

    撞墙记录:
        1. MSMF 高帧率必须 MJPG，否则驱动协商降回低帧率
        2. 设置顺序: 分辨率 -> FOURCC -> FPS。乱序则 MSMF 高帧率无效
        3. set() 是请求不是命令，必须 read 一帧触发协商再 get 读回真实值
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    camera_id: int = Field(default=0, ge=0, description="OpenCV 设备 ID")
    width: int = Field(default=1280, gt=0, le=7680, description="请求分辨率宽")
    height: int = Field(default=720, gt=0, le=4320, description="请求分辨率高")
    fps: int = Field(default=30, gt=0, le=1000, description="请求帧率")
    backend: CameraBackend = Field(default="any", description="后端: msmf/dshow/v4l2")
    codec: CameraCodec = Field(default="MJPG", description="FOURCC 编码")
    auto_exposure: float = Field(default=-1, description="自动曝光（-1=不设置）")
    brightness: int = Field(default=-1, description="亮度（-1=不设置）")

    def get_resolution(self) -> tuple[int, int, int]:
        return (self.width, self.height, self.fps)
