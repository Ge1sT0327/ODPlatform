"""推理配置模型。"""

from pydantic import Field
from odp_platform.runtime_config.base_config import BaseConfig

class YOLOInferConfig(BaseConfig):
    task: str = Field(default="detect", json_schema_extra={"group": "任务标识"})
    experiment_name: str = Field(default="infer", json_schema_extra={"group": "任务标识"})

    # 输入源（必填特征：与 train/val 的关键差异）
    source: str = Field(
        ...,
        json_schema_extra={"group": "输入", "description": "输入源: 0=摄像头, path/to/img.jpg, path/to/video.mp4, rtsp://..."}
    )

    # 推理参数
    imgsz: int = Field(default=640, json_schema_extra={"group": "推理参数"})
    conf: float = Field(default=0.25, json_schema_extra={"group": "推理参数", "description": "置信度阈值"})
    iou: float = Field(default=0.7, json_schema_extra={"group": "推理参数", "description": "NMS IoU 阈值"})
    device: str = Field(default="auto", json_schema_extra={"group": "推理参数"})

    # 输出控制
    show: bool = Field(default=False, json_schema_extra={"group": "输出", "description": "是否实时显示"})
    save: bool = Field(default=False, json_schema_extra={"group": "输出", "description": "是否保存输出"})
    save_dir: str = Field(default="", json_schema_extra={"group": "输出"})

    def to_ultralytics_kwargs(self) -> dict:
        return {
            "source": self.source,
            "imgsz": self.imgsz,
            "conf": self.conf,
            "iou": self.iou,
            "device": self.device,
            "show": self.show,
            "save": self.save,
            "project": "runs",
            "name": self.experiment_name,
            "exist_ok": True,
        }
