"""odp-eval 命令入口。"""

import sys
import argparse
from odp_platform.evaluation.service import evaluate_yolo
from odp_platform.common.constants import ExitCode

def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description="评估目标检测模型")
    parser.add_argument("--weights", required=True, help="权重文件路径或名称")
    parser.add_argument("--data", default="safety_helmet.yaml", help="数据集配置")
    parser.add_argument("--yaml", default=None, help="评估配置 YAML")
    parser.add_argument("--imgsz", type=int, help="输入尺寸")
    parser.add_argument("--device", help="设备")
    args = parser.parse_args(argv)

    overrides = {k: v for k, v in [("imgsz", args.imgsz), ("device", args.device)] if v is not None}
    result = evaluate_yolo(
        weights=args.weights,
        data=args.data,
        config_path=args.yaml,
        **overrides,
    )

    if result.success:
        m = result.metrics
        print(f"mAP50: {m.mAP50:.4f}  mAP50-95: {m.mAP50_95:.4f}")
        print(f"Precision: {m.precision:.4f}  Recall: {m.recall:.4f}")
        return ExitCode.SUCCESS
    else:
        print(f"评估失败: {result.error}", file=sys.stderr)
        return ExitCode.USER_ERROR

if __name__ == "__main__":
    sys.exit(main())
