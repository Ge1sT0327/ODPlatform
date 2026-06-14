"""检查 data.yaml 字段齐备与合法性。"""

import yaml
from odp_platform.data_validation.registry import check, CheckContext, CheckResult, CheckSeverity

@check("yaml_schema")
def check_yaml_schema(ctx: CheckContext) -> CheckResult:
    """
    检查 data.yaml 是否包含必要字段: path, train, val, nc, names。
    nc > 0, names 长度 == nc, train/val 路径存在。
    """
    try:
        config = yaml.safe_load(ctx.yaml_path.read_text(encoding="utf-8"))
    except Exception as e:
        return CheckResult(
            check_name="yaml_schema",
            severity=CheckSeverity.ERROR,
            message=f"无法解析 data.yaml: {e}",
        )

    issues = []
    required = ["path", "train", "val", "nc", "names"]
    for field in required:
        if field not in config:
            issues.append(f"缺少字段: {field}")

    nc = config.get("nc", 0)
    if nc <= 0:
        issues.append(f"nc 必须 > 0，当前: {nc}")

    names = config.get("names", {})
    if len(names) != nc:
        issues.append(f"names 数量 ({len(names)}) != nc ({nc})")

    # 检查 train/val 路径
    base = config.get("path", ".")
    from pathlib import Path
    for split in ["train", "val"]:
        sp = Path(base) / config.get(split, "")
        if not sp.exists():
            issues.append(f"{split} 路径不存在: {sp}")

    if issues:
        return CheckResult(
            check_name="yaml_schema",
            severity=CheckSeverity.ERROR,
            message=f"data.yaml 有 {len(issues)} 个问题",
            details={"issues": issues},
        )
    return CheckResult(
        check_name="yaml_schema",
        severity=CheckSeverity.INFO,
        message="data.yaml 格式正确",
        details={"nc": nc, "names": list(names.values()) if isinstance(names, dict) else names},
    )
