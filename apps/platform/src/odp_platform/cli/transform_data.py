"""odp-transform 命令入口。"""

import sys
import argparse
from odp_platform.data_pipeline.orchestrator import DatasetPipeline
from odp_platform.common.constants import ExitCode, DEFAULT_DATASET
from odp_platform.common.logging_utils import get_logger

def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description="原始数据 → YOLO 格式 + 切分")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="数据集名称")
    parser.add_argument("--format", default="pascal_voc", choices=["pascal_voc", "coco", "yolo"], help="源标注格式")
    parser.add_argument("--split-ratio", nargs=3, type=float, default=[0.8, 0.1, 0.1], metavar=("TRAIN", "VAL", "TEST"))
    parser.add_argument("--strategy", default="random", choices=["random", "stratified"])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--classes", nargs="*", help="类别名列表（如 hat person）")
    args = parser.parse_args(argv)

    logger = get_logger("transform_data", log_type="transform")
    logger.info(f"开始数据流水线: dataset={args.dataset}, format={args.format}")

    pipeline = DatasetPipeline()
    result = pipeline.run(
        dataset_name=args.dataset,
        source_format=args.format,
        class_names=args.classes,
        split_ratios=args.split_ratio,
        split_strategy=args.strategy,
        seed=args.seed,
    )

    if not result.success:
        logger.error(f"数据流水线失败: {result.error}")
        return ExitCode.USER_ERROR

    logger.info(f"转换完成: {result.convert.total_labels} 个标注文件")
    logger.info(f"切分完成: train={len(result.split.train)}, val={len(result.split.val)}, test={len(result.split.test)}")
    logger.info(f"data.yaml → {result.dataset_yaml_path}")
    return ExitCode.SUCCESS

if __name__ == "__main__":
    sys.exit(main())
