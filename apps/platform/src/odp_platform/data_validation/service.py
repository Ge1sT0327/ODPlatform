"""聚合执行引擎 + validate_dataset 端到端入口。"""

from datetime import datetime
from pathlib import Path
from odp_platform.data_validation.registry import (
    CheckContext, CheckResult, CheckSeverity,
    get_all_checks,
)
from odp_platform.data_validation.snapshot import build_snapshot
from odp_platform.data_validation.report import ValidationReport
from odp_platform.common.paths import dataset_yaml_path, validation_run_dir

# 触发检查注册
import odp_platform.data_validation.checks  # noqa: F401

def run_all_checks(ctx: CheckContext) -> list:
    """
    聚合执行全部已注册检查。
    每个检查独立执行，异常被捕获为 ERROR CheckResult。
    返回完整的 CheckResult 列表（全部执行完毕才返回）。
    """
    results = []
    for name, func in get_all_checks().items():
        try:
            result = func(ctx)
        except Exception as e:
            result = CheckResult(
                check_name=name,
                severity=CheckSeverity.ERROR,
                message=f"检查 '{name}' 执行异常: {e}",
            )
        results.append(result)
    return results

def validate_dataset(
    dataset_name: str,
    task: str = "detect",
    split: str = "all",
) -> ValidationReport:
    """
    端到端数据验证入口。

    1. 解析 yaml 路径
    2. build_snapshot（一次扫盘）
    3. 构建 CheckContext
    4. run_all_checks（聚合执行）
    5. 生成 ValidationReport
    6. 报告落盘到 runs/data_validation/<run_id>/
    """
    yaml_path = dataset_yaml_path(dataset_name)
    if not yaml_path.exists():
        return ValidationReport(
            dataset_name=dataset_name,
            task_type=task,
            split=split,
            total_checks=0,
            results=[],
            overall_severity=CheckSeverity.ERROR,
            summary={"ERROR": 1},
            error=f"数据集配置不存在: {yaml_path}",
        )

    snapshot = build_snapshot(yaml_path, dataset_name)
    ctx = CheckContext(
        yaml_path=yaml_path,
        dataset_name=dataset_name,
        task_type=task,
        snapshot=snapshot,
    )
    results = run_all_checks(ctx)

    overall = CheckSeverity.INFO
    for r in results:
        if r.severity == CheckSeverity.ERROR:
            overall = CheckSeverity.ERROR
        elif r.severity == CheckSeverity.WARNING and overall != CheckSeverity.ERROR:
            overall = CheckSeverity.WARNING

    summary = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for r in results:
        summary[r.severity.value] += 1

    report = ValidationReport(
        dataset_name=dataset_name,
        task_type=task,
        split=split,
        total_checks=len(results),
        results=results,
        overall_severity=overall,
        summary=summary,
    )

    # 报告落盘
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = validation_run_dir(run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    import json
    (run_dir / "report.json").write_text(
        report.to_json(), encoding="utf-8"
    )

    return report
