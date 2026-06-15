"""通用结果指标对象（供 training 和 evaluation 复用）。"""

from dataclasses import dataclass

@dataclass(frozen=True)
class ResultMetrics:
    """目标检测评估指标。"""
    mAP50: float = 0.0
    mAP50_95: float = 0.0
    precision: float = 0.0
    recall: float = 0.0

    def to_dict(self) -> dict:
        return {
            "mAP50": self.mAP50,
            "mAP50_95": self.mAP50_95,
            "precision": self.precision,
            "recall": self.recall,
        }
