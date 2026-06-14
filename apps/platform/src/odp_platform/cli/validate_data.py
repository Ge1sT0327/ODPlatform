"""odp-validate 命令入口。"""

import sys
import argparse
from odp_platform.data_validation.service import validate_dataset
from odp_platform.data_validation.render import render_to_logger
from odp_platform.data_validation.registry import CheckSeverity
from odp_platform.common.constants import DEFAULT_DATASET, ValidationExitCode
from odp_platform.common.logging_utils import get_logger

def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description="训练前数据质检")
    parser.add_argument("--dataset", default=DEFAULT_DATASET, help="数据集名称")
    parser.add_argument("--task", default="detect", help="任务类型 (detect/segment)")
    parser.add_argument("--split", default="all", help="切分 (all/train/val)")
    args = parser.parse_args(argv)

    logger = get_logger("validate_data", log_type="validate")
    logger.info(f"开始数据验证: dataset={args.dataset}, task={args.task}")

    report = validate_dataset(
        dataset_name=args.dataset,
        task=args.task,
        split=args.split,
    )

    render_to_logger(report, logger)

    if report.overall_severity == CheckSeverity.ERROR:
        return ValidationExitCode.ERROR
    elif report.overall_severity == CheckSeverity.WARNING:
        return ValidationExitCode.WARNING
    return ValidationExitCode.PASS

if __name__ == "__main__":
    sys.exit(main())
