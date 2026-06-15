"""验证/评估配置模型。"""

from pydantic import Field
from odp_platform.runtime_config.base_config import BaseConfig

class YOLOValConfig(BaseConfig):
    # 任务标识
    task: str = Field(default="detect", json_schema_extra={"group": "任务标识"})
    experiment_name: str = Field(default="eval", json_schema_extra={"group": "任务标识"})

    # 数据
    data: str = Field(default="safety_helmet.yaml", json_schema_extra={"group": "数据"})

    # 评估参数
    imgsz: int = Field(default=640, json_schema_extra={"group": "评估参数"})
    batch: int = Field(default=16, json_schema_extra={"group": "评估参数"})
    device: str = Field(default="auto", json_schema_extra={"group": "评估参数"})
    workers: int = Field(default=8, json_schema_extra={"group": "评估参数"})
    conf: float = Field(default=0.001, json_schema_extra={"group": "评估参数", "description": "置信度阈值"})
    iou: float = Field(default=0.6, json_schema_extra={"group": "评估参数", "description": "IoU 阈值"})

    def to_ultralytics_kwargs(self) -> dict:
        return {
            "data": self.data,
            "imgsz": self.imgsz,
            "batch": self.batch,
            "device": self.device,
            "workers": self.workers,
            "conf": self.conf,
            "iou": self.iou,
            "project": "runs",
            "name": self.experiment_name,
            "exist_ok": True,
        }
