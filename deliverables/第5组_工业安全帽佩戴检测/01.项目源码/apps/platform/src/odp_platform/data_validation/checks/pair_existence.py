"""图片↔标注一一对应检查。"""

from odp_platform.data_validation.registry import check, CheckContext, CheckResult, CheckSeverity
from odp_platform.common.constants import PAIR_MISSING_INFO_THRESHOLD, PAIR_MISSING_WARN_THRESHOLD

@check("pair_existence")
def check_pair_existence(ctx: CheckContext) -> CheckResult:
    """
    检查每个切分中图片与标注是否一一对应。
    统计: 图片无标注 (orphan_images)、标注无图片 (orphan_labels)。
    按缺失比例分级: <1% INFO, 1%~5% WARNING, >5% ERROR。
    """
    if ctx.snapshot is None:
        return CheckResult(check_name="pair_existence", severity=CheckSeverity.ERROR,
                           message="需要 DatasetSnapshot，请先 build_snapshot")

    details = {}
    max_missing_ratio = 0.0
    for name, ss in ctx.snapshot.splits.items():
        img_only = ss.image_files - ss.label_files
        lbl_only = ss.label_files - ss.image_files
        total = len(ss.image_files) + len(ss.label_files)
        if total == 0:
            continue
        ratio = (len(img_only) + len(lbl_only)) / total
        max_missing_ratio = max(max_missing_ratio, ratio)
        details[name] = {
            "orphan_images": sorted(img_only)[:20],    # 最多列举 20 个
            "orphan_labels": sorted(lbl_only)[:20],
            "orphan_image_count": len(img_only),
            "orphan_label_count": len(lbl_only),
            "total_images": len(ss.image_files),
            "total_labels": len(ss.label_files),
        }

    if max_missing_ratio > PAIR_MISSING_WARN_THRESHOLD:
        sev = CheckSeverity.ERROR
    elif max_missing_ratio > PAIR_MISSING_INFO_THRESHOLD:
        sev = CheckSeverity.WARNING
    else:
        sev = CheckSeverity.INFO

    return CheckResult(
        check_name="pair_existence",
        severity=sev,
        message=f"配对缺失比例: {max_missing_ratio:.2%}",
        details=details,
    )
