"""标签格式检查：坐标合法性、类别 id 不越界。"""

from pathlib import Path
from odp_platform.data_validation.registry import check, CheckContext, CheckResult, CheckSeverity

@check("label_format")
def check_label_format(ctx: CheckContext) -> CheckResult:
    """
    检查每个 label txt 文件:
    - 每行必须有 5 个字段
    - 类别 id >= 0 且 < nc
    - 坐标在 [0, 1] 范围内
    """
    if ctx.snapshot is None:
        return CheckResult(
            check_name="label_format",
            severity=CheckSeverity.ERROR,
            message="需要 DatasetSnapshot",
        )

    nc = ctx.snapshot.nc
    bad_files = []
    out_of_range = 0
    bad_class = 0
    bad_lines = 0

    for name, ss in ctx.snapshot.splits.items():
        for lbl_stem in ss.label_files:
            lbl_path = ss.labels_dir / f"{lbl_stem}.txt"
            if not lbl_path.exists():
                continue
            lines = lbl_path.read_text(encoding="utf-8").strip().split("\n")
            for i, line in enumerate(lines):
                if not line.strip():
                    continue
                parts = line.strip().split()
                if len(parts) != 5:
                    bad_lines += 1
                    bad_files.append(str(lbl_path))
                    break
                try:
                    cid, cx, cy, w, h = map(float, parts)
                except ValueError:
                    bad_lines += 1
                    bad_files.append(str(lbl_path))
                    break
                cid = int(cid)
                if cid < 0 or (nc > 0 and cid >= nc):
                    bad_class += 1
                if not (0 <= cx <= 1 and 0 <= cy <= 1 and 0 <= w <= 1 and 0 <= h <= 1):
                    out_of_range += 1

    total_issues = bad_lines + bad_class + out_of_range
    if total_issues == 0:
        return CheckResult(
            check_name="label_format",
            severity=CheckSeverity.INFO,
            message="所有标注格式正确",
        )

    sev = CheckSeverity.ERROR if bad_lines > 0 or bad_class > 0 else CheckSeverity.WARNING
    return CheckResult(
        check_name="label_format",
        severity=sev,
        message=f"标注问题: {total_issues} 处 (格式错误={bad_lines}, 类别越界={bad_class}, 坐标越界={out_of_range})",
        details={
            "bad_line_count": bad_lines,
            "bad_class_count": bad_class,
            "out_of_range_count": out_of_range,
            "affected_files": bad_files[:20],
        },
    )
