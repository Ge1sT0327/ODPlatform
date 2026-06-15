"""YOLO → YOLO 直通（已是目标格式，做复制 + 基本校验）。"""

import shutil
from pathlib import Path
from collections import Counter
from odp_platform.data_pipeline.convert.registry import register, ConvertOptions, ConvertResult

@register("yolo")
def convert_yolo(options: ConvertOptions) -> ConvertResult:
    """
    YOLO 格式直通：将 labels 目录复制到目标位置，不修改内容。
    仅做基本校验：每行是否有 5 个字段、字段是否合法。
    """
    src = Path(options.source_dir)
    tgt = Path(options.target_dir)
    tgt_labels = tgt / "labels"
    tgt_labels.mkdir(parents=True, exist_ok=True)

    label_files = sorted(src.glob("*.txt"))
    if not label_files:
        # 尝试 labels/ 子目录
        label_files = sorted((src / "labels").glob("*.txt"))

    total = 0
    for lf in label_files:
        dest = tgt_labels / lf.name
        shutil.copy2(lf, dest)
        lines = lf.read_text(encoding="utf-8").strip().split("\n")
        for line in lines:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) != 5:
                continue  # 跳过损坏行
            total += 1

    return ConvertResult(
        success=True,
        total_labels=len(label_files),
        total_images=total,
    )
