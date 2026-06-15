"""切分唯一性：同一样本不得同时出现在多个切分。"""

from odp_platform.data_validation.registry import check, CheckContext, CheckResult, CheckSeverity

@check("split_uniqueness")
def check_split_uniqueness(ctx: CheckContext) -> CheckResult:
    """
    检查 train/val/test 的图片文件名是否有交集。
    任一交集即为 ERROR。
    """
    if ctx.snapshot is None:
        return CheckResult(
            check_name="split_uniqueness",
            severity=CheckSeverity.ERROR,
            message="需要 DatasetSnapshot",
        )

    names = list(ctx.snapshot.splits.keys())
    overlaps = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a = ctx.snapshot.splits[names[i]].image_files
            b = ctx.snapshot.splits[names[j]].image_files
            common = a & b
            if common:
                overlaps[f"{names[i]}_{names[j]}"] = sorted(common)

    if overlaps:
        total = sum(len(v) for v in overlaps.values())
        return CheckResult(
            check_name="split_uniqueness",
            severity=CheckSeverity.ERROR,
            message=f"发现 {total} 个样本同时出现在多个切分中",
            details={"overlaps": overlaps},
        )

    return CheckResult(
        check_name="split_uniqueness",
        severity=CheckSeverity.INFO,
        message="切分无重叠",
    )
