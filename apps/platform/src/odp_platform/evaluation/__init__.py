"""evaluation 子系统对外公共 API（仅 4 符号）。"""

from odp_platform.evaluation.service import ValService, ValResult, ValMetrics, evaluate_yolo

__all__ = ["ValService", "ValResult", "ValMetrics", "evaluate_yolo"]
