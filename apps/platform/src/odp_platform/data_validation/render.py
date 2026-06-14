"""报告渲染：将 ValidationReport 输出到日志/控制台。"""

import logging
from odp_platform.data_validation.report import ValidationReport
from odp_platform.data_validation.registry import CheckSeverity
from odp_platform.common.string_utils import format_table_row, format_table_separator

SEVERITY_MARKS = {
    CheckSeverity.ERROR: "❌",
    CheckSeverity.WARNING: "⚠️",
    CheckSeverity.INFO: "✅",
}

def render_to_logger(report: ValidationReport, logger: logging.Logger) -> None:
    """分段渲染 ValidationReport 到 logger。"""
    logger.info("=" * 60)
    logger.info(f"  数据集质检报告: {report.dataset_name}")
    logger.info(f"  任务类型: {report.task_type}  切分: {report.split}")
    logger.info(f"  整体判定: {report.overall_severity.value}")

    if report.error:
        logger.error(f"  错误: {report.error}")
        return

    widths = [20, 10, 50]
    logger.info(format_table_separator(widths))
    logger.info(format_table_row(["检查项", "结果", "说明"], widths))
    logger.info(format_table_separator(widths))

    for r in report.results:
        mark = SEVERITY_MARKS.get(r.severity, "")
        logger.info(format_table_row(
            [r.check_name, f"{mark} {r.severity.value}", r.message],
            widths,
            ["left", "left", "left"],
        ))

    logger.info(format_table_separator(widths))
    logger.info(f"  汇总: ERROR={report.summary.get('ERROR',0)} "
                f"WARNING={report.summary.get('WARNING',0)} "
                f"INFO={report.summary.get('INFO',0)}")
    logger.info("=" * 60)
