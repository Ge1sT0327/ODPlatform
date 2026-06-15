"""训练编排器：配置→校验→日志→底层训练→归档→审计。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime
import json
import shutil

from odp_platform.runtime_config.train_config import YOLOTrainConfig
from odp_platform.runtime_config import build_train_config
from odp_platform.common.result import ResultMetrics
from odp_platform.common.logging_utils import get_logger
from odp_platform.common.model_utils import resolve_model_path, resolve_dataset_path, rename_log_to_save_dir
from odp_platform.common.config_log import log_effective_config
from odp_platform.common.system_utils import get_system_info
from odp_platform.common.paths import CHECKPOINTS_DIR
from odp_platform.data_validation.registry import CheckSeverity

@dataclass(frozen=True)
class TrainMetrics(ResultMetrics):
    """训练指标（继承通用 ResultMetrics）。"""
    pass

@dataclass(frozen=True)
class TrainResult:
    success: bool
    error: Optional[str] = None
    metrics: Optional[TrainMetrics] = None
    best_pt_path: Optional[Path] = None
    last_pt_path: Optional[Path] = None
    run_dir: Optional[Path] = None
    audit_path: Optional[Path] = None

class TrainService:
    """训练编排器。不发明算法，只串联已有工具。"""

    def __init__(self, config: YOLOTrainConfig):
        self.config = config
        self.logger = get_logger("training", log_type="train")

    def train(self, skip_pre_validate: bool = False, academic_plots: bool = False) -> TrainResult:
        """
        编排主流程:
        1. 日志生效配置
        2. (可选) 数据验证
        3. 解析模型/数据集路径
        4. 底层训练
        5. 归档权重
        6. 写审计快照
        异常兜底为 TrainResult.error，不让 traceback 穿透。
        """
        try:
            # 0. 可选学术风格
            if academic_plots:
                from odp_platform.common.plot_style import apply_academic_style
                apply_academic_style()

            # 1. 日志生效配置
            log_effective_config(self.config, self.logger)
            self.logger.info(f"设备信息: {get_system_info()}")

            # 2. 训练前数据校验
            if not skip_pre_validate:
                from odp_platform.data_validation.service import validate_dataset
                report = validate_dataset(
                    dataset_name=self.config.data.replace(".yaml", ""),
                    task=self.config.task,
                )
                if report.overall_severity == CheckSeverity.ERROR:
                    return TrainResult(
                        success=False,
                        error=f"数据验证不通过（{report.summary.get('ERROR', 0)} 个 ERROR）。请先修复或使用 --no-pre-validate 跳过。"
                    )
                self.logger.info("数据验证通过。")

            # 3. 解析路径
            model_path = resolve_model_path(self.config.model)
            data_path = resolve_dataset_path(self.config.data)
            self.logger.info(f"模型: {model_path}, 数据: {data_path}")

            # 4. 训练
            from ultralytics import YOLO
            model = YOLO(str(model_path))
            kwargs = self.config.to_ultralytics_kwargs()
            kwargs["data"] = str(data_path)
            results = model.train(**kwargs)

            # 5. 归档权重
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            exp_name = self.config.experiment_name
            run_dir = Path(results.save_dir) if hasattr(results, "save_dir") else Path(f"runs/detect/{exp_name}")

            best_src = run_dir / "weights" / "best.pt"
            last_src = run_dir / "weights" / "last.pt"
            best_dst = CHECKPOINTS_DIR / f"{exp_name}_{ts}_best.pt"
            last_dst = CHECKPOINTS_DIR / f"{exp_name}_{ts}_last.pt"

            best_dst.parent.mkdir(parents=True, exist_ok=True)
            if best_src.exists():
                shutil.copy2(best_src, best_dst)
            if last_src.exists():
                shutil.copy2(last_src, last_dst)

            # 6. 审计快照
            audit_path = run_dir / "odp_audit.json"
            audit = {
                "timestamp": ts,
                "config": self.config.to_audit_snapshot(),
                "weights": {
                    "best": str(best_dst),
                    "last": str(last_dst),
                },
                "environment": get_system_info(),
                "framework": "ultralytics",
            }
            audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

            # 7. 日志名对齐
            rename_log_to_save_dir("training", run_dir)

            # 收集指标
            metrics = TrainMetrics(
                mAP50=float(results.results_dict.get("metrics/mAP50(B)", 0) or 0),
                mAP50_95=float(results.results_dict.get("metrics/mAP50-95(B)", 0) or 0),
                precision=float(results.results_dict.get("metrics/precision(B)", 0) or 0),
                recall=float(results.results_dict.get("metrics/recall(B)", 0) or 0),
            )

            self.logger.info(f"训练完成: best={best_dst}, mAP50={metrics.mAP50:.4f}")
            return TrainResult(
                success=True,
                metrics=metrics,
                best_pt_path=best_dst,
                last_pt_path=last_dst,
                run_dir=run_dir,
                audit_path=audit_path,
            )
        except Exception as e:
            self.logger.error(f"训练失败: {e}", exc_info=True)
            return TrainResult(success=False, error=str(e))

def train_yolo(
    config_path: str = None,
    cli_overrides: dict = None,
    skip_pre_validate: bool = False,
    academic_plots: bool = False,
) -> TrainResult:
    """便捷函数：构建配置 → new TrainService → train()。"""
    config = build_train_config(config_path, cli_overrides)
    return TrainService(config).train(
        skip_pre_validate=skip_pre_validate,
        academic_plots=academic_plots,
    )
