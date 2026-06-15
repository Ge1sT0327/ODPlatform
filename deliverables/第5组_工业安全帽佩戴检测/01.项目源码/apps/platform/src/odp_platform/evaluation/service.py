"""评估编排器：配置→解析权重→验证→指标。仅 1 文件 + __init__。"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from odp_platform.runtime_config.val_config import YOLOValConfig
from odp_platform.runtime_config import build_val_config
from odp_platform.common.result import ResultMetrics
from odp_platform.common.logging_utils import get_logger
from odp_platform.common.model_utils import resolve_model_path, resolve_dataset_path
from odp_platform.common.paths import CHECKPOINTS_DIR

@dataclass(frozen=True)
class ValMetrics(ResultMetrics):
    pass

@dataclass(frozen=True)
class ValResult:
    success: bool
    error: Optional[str] = None
    metrics: Optional[ValMetrics] = None

class ValService:
    """评估编排器。不 import training，复用全部走 common。"""

    def __init__(self, config: YOLOValConfig = None):
        self.config = config or YOLOValConfig()
        self.logger = get_logger("evaluation", log_type="eval")

    def evaluate(self, weights: str, data: str) -> ValResult:
        """
        1. 解析权重 — 优先 CHECKPOINTS_DIR
        2. 解析数据集路径
        3. 调 ultralytics model.val()
        4. 收集指标
        异常兜底为 ValResult.error。
        """
        try:
            # 1. 解析权重（优先 CHECKPOINTS_DIR）
            weights_path = resolve_model_path(weights, search_dirs=[CHECKPOINTS_DIR])
            data_path = resolve_dataset_path(data)
            self.logger.info(f"评估: weights={weights_path}, data={data_path}")

            # 2. 调底层引擎
            from ultralytics import YOLO
            model = YOLO(str(weights_path))
            kwargs = self.config.to_ultralytics_kwargs()
            kwargs["data"] = str(data_path)
            results = model.val(**kwargs)

            # 3. 收集指标
            metrics = ValMetrics(
                mAP50=float(results.results_dict.get("metrics/mAP50(B)", 0) or 0),
                mAP50_95=float(results.results_dict.get("metrics/mAP50-95(B)", 0) or 0),
                precision=float(results.results_dict.get("metrics/precision(B)", 0) or 0),
                recall=float(results.results_dict.get("metrics/recall(B)", 0) or 0),
            )
            self.logger.info(f"评估完成: mAP50={metrics.mAP50:.4f}, mAP50-95={metrics.mAP50_95:.4f}")
            return ValResult(success=True, metrics=metrics)
        except Exception as e:
            self.logger.error(f"评估失败: {e}", exc_info=True)
            return ValResult(success=False, error=str(e))

def evaluate_yolo(
    weights: str,
    data: str,
    config_path: str = None,
    **overrides,
) -> ValResult:
    config = build_val_config(config_path, overrides) if config_path else YOLOValConfig(**overrides)
    return ValService(config).evaluate(weights=weights, data=data)
