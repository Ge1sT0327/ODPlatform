"""类别平衡分析报告。"""

from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path
from collections import Counter
from odp_platform.common.paths import TRAIN_LABELS_DIR, VAL_LABELS_DIR

@dataclass
class ClassStat:
    class_id: int
    class_name: str
    count: int
    percentage: float

@dataclass
class ClassBalanceReport:
    dataset_name: str
    split: str
    total_instances: int
    classes: List[ClassStat]

def analyze_class_balance(
    labels_dir: Path,
    class_names: List[str] = None,
) -> ClassBalanceReport:
    """
    统计 labels_dir 下所有 txt 文件中的类别分布。
    返回 ClassBalanceReport。
    """
    counter = Counter()
    for lbl in sorted(labels_dir.glob("*.txt")):
        for line in lbl.read_text(encoding="utf-8").strip().split("\n"):
            if not line.strip():
                continue
            cls_id = int(line.strip().split()[0])
            counter[cls_id] += 1

    total = sum(counter.values())
    classes = []
    for cid in sorted(counter.keys()):
        name = class_names[cid] if class_names and cid < len(class_names) else str(cid)
        classes.append(ClassStat(
            class_id=cid,
            class_name=name,
            count=counter[cid],
            percentage=(counter[cid] / total * 100) if total > 0 else 0,
        ))

    return ClassBalanceReport(
        dataset_name=labels_dir.parent.name,
        split=labels_dir.parent.name,
        total_instances=total,
        classes=classes,
    )

def render_balance_report(report: ClassBalanceReport) -> str:
    """将 ClassBalanceReport 渲染为可读字符串表格。"""
    from odp_platform.common.string_utils import format_table_row, format_table_separator
    widths = [8, 16, 8, 10]
    lines = [
        f"类别平衡报告 - {report.dataset_name}/{report.split}",
        f"总标注实例数: {report.total_instances}",
        format_table_separator(widths),
        format_table_row(["ID", "类别名", "数量", "占比%"], widths),
        format_table_separator(widths),
    ]
    for c in report.classes:
        lines.append(format_table_row(
            [str(c.class_id), c.class_name, str(c.count), f"{c.percentage:.1f}"],
            widths,
            ["right", "left", "right", "right"],
        ))
    lines.append(format_table_separator(widths))
    return "\n".join(lines)
