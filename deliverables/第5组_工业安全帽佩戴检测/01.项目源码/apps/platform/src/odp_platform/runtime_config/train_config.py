"""训练配置模型。"""

from typing import Optional, List, Literal
from pydantic import Field
from odp_platform.runtime_config.base_config import BaseConfig

class YOLOTrainConfig(BaseConfig):
    # ---- 任务标识 ----
    task: str = Field(
        default="detect",
        json_schema_extra={"group": "任务标识", "example": "detect", "description": "任务类型: detect, segment, classify"}
    )
    experiment_name: str = Field(
        default="exp",
        json_schema_extra={"group": "任务标识", "example": "safety_helmet_v1", "description": "实验名称（用于命名产出）"}
    )

    # ---- 数据 ----
    data: str = Field(
        default="safety_helmet.yaml",
        json_schema_extra={"group": "数据", "example": "safety_helmet.yaml", "description": "数据集配置文件名"}
    )

    # ---- 模型 ----
    model: str = Field(
        default="yolov8n.pt",
        json_schema_extra={"group": "模型", "example": "yolov8n.pt", "description": "预训练权重名或路径"}
    )

    # ---- 训练参数 ----
    epochs: int = Field(
        default=100, ge=1,
        json_schema_extra={"group": "训练参数", "description": "训练轮数"}
    )
    imgsz: int = Field(
        default=640, ge=32,
        json_schema_extra={"group": "训练参数", "description": "输入图像尺寸（须为32的倍数）"}
    )
    batch: int = Field(
        default=16, ge=1,
        json_schema_extra={"group": "训练参数", "description": "批大小"}
    )
    device: str = Field(
        default="auto",
        json_schema_extra={"group": "训练参数", "example": "cpu, 0, 0,1", "description": "训练设备"}
    )
    workers: int = Field(
        default=8, ge=0,
        json_schema_extra={"group": "训练参数", "description": "数据加载线程数"}
    )

    # ---- 优化器 ----
    lr0: float = Field(
        default=0.01, gt=0,
        json_schema_extra={"group": "优化器", "description": "初始学习率"}
    )
    lrf: float = Field(
        default=0.01, gt=0,
        json_schema_extra={"group": "优化器", "description": "最终学习率因子 (lr0 * lrf)"}
    )
    momentum: float = Field(
        default=0.937, gt=0,
        json_schema_extra={"group": "优化器", "description": "SGD momentum / Adam beta1"}
    )
    weight_decay: float = Field(
        default=0.0005, ge=0,
        json_schema_extra={"group": "优化器", "description": "权重衰减"}
    )
    optimizer: str = Field(
        default="auto",
        json_schema_extra={"group": "优化器", "description": "优化器: auto, SGD, Adam, AdamW"}
    )

    # ---- 数据增强 ----
    hsv_h: float = Field(default=0.015, json_schema_extra={"group": "数据增强"})
    hsv_s: float = Field(default=0.7, json_schema_extra={"group": "数据增强"})
    hsv_v: float = Field(default=0.4, json_schema_extra={"group": "数据增强"})
    degrees: float = Field(default=0.0, json_schema_extra={"group": "数据增强"})
    translate: float = Field(default=0.1, json_schema_extra={"group": "数据增强"})
    scale: float = Field(default=0.5, json_schema_extra={"group": "数据增强"})
    fliplr: float = Field(default=0.5, json_schema_extra={"group": "数据增强"})
    mosaic: float = Field(default=1.0, json_schema_extra={"group": "数据增强"})

    def to_ultralytics_kwargs(self) -> dict:
        """转为 ultralytics model.train() 关键字参数。"""
        return {
            "data": self.data,
            "model": self.model,
            "epochs": self.epochs,
            "imgsz": self.imgsz,
            "batch": self.batch,
            "device": self.device,
            "workers": self.workers,
            "lr0": self.lr0,
            "lrf": self.lrf,
            "momentum": self.momentum,
            "weight_decay": self.weight_decay,
            "optimizer": self.optimizer,
            "hsv_h": self.hsv_h,
            "hsv_s": self.hsv_s,
            "hsv_v": self.hsv_v,
            "degrees": self.degrees,
            "translate": self.translate,
            "scale": self.scale,
            "fliplr": self.fliplr,
            "mosaic": self.mosaic,
            "project": "runs",
            "name": self.experiment_name,
            "exist_ok": True,
        }
