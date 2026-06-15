"""training 子系统对外公共 API（仅 4 符号）。"""

from odp_platform.training.service import TrainService, TrainResult, TrainMetrics, train_yolo

__all__ = ["TrainService", "TrainResult", "TrainMetrics", "train_yolo"]
