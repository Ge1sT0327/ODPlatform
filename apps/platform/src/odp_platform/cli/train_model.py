"""odp-train 命令入口。"""

import sys
import argparse
from odp_platform.training.service import train_yolo
from odp_platform.common.constants import ExitCode

def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description="训练目标检测模型")
    parser.add_argument("--config", default=None, help="训练配置 YAML 路径")
    parser.add_argument("--epochs", type=int, help="训练轮数（覆盖配置）")
    parser.add_argument("--batch", type=int, help="批大小（覆盖配置）")
    parser.add_argument("--imgsz", type=int, help="输入尺寸（覆盖配置）")
    parser.add_argument("--device", help="设备（覆盖配置）")
    parser.add_argument("--model", help="预训练权重（覆盖配置）")
    parser.add_argument("--data", help="数据集配置（覆盖配置）")
    parser.add_argument("--no-pre-validate", action="store_true", help="跳过训练前数据校验")
    parser.add_argument("--academic-plots", action="store_true", help="使用学术绘图风格")
    args = parser.parse_args(argv)

    overrides = {k: v for k, v in vars(args).items()
                 if k not in ("config", "no_pre_validate", "academic_plots") and v is not None}

    result = train_yolo(
        config_path=args.config,
        cli_overrides=overrides,
        skip_pre_validate=args.no_pre_validate,
        academic_plots=args.academic_plots,
    )

    if result.success:
        print(f"训练成功! best.pt → {result.best_pt_path}")
        print(f"mAP50: {result.metrics.mAP50:.4f}, mAP50-95: {result.metrics.mAP50_95:.4f}")
        return ExitCode.SUCCESS
    else:
        print(f"训练失败: {result.error}", file=sys.stderr)
        return ExitCode.USER_ERROR

if __name__ == "__main__":
    sys.exit(main())
