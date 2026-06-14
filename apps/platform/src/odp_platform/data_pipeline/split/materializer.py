"""将切分结果物化到磁盘（复制文件到 data/{train,val,test}/）。"""

import shutil
from pathlib import Path
from typing import List
from odp_platform.data_pipeline.split.splitter import SplitResult
from odp_platform.common.paths import (
    TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR,
    VAL_IMAGES_DIR, VAL_LABELS_DIR,
    TEST_IMAGES_DIR, TEST_LABELS_DIR,
)

def materialize_split(split: SplitResult, dry_run: bool = False) -> dict:
    """
    将 train/val/test 图片和标注复制到对应目录。
    返回 {"train": count, "val": count, "test": count}。
    dry_run=True 时只统计不复制。
    """
    mapping = [
        ("train", TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR),
        ("val", VAL_IMAGES_DIR, VAL_LABELS_DIR),
        ("test", TEST_IMAGES_DIR, TEST_LABELS_DIR),
    ]
    counts = {}
    for name, img_dir, lbl_dir in mapping:
        img_dir.mkdir(parents=True, exist_ok=True)
        lbl_dir.mkdir(parents=True, exist_ok=True)
        pairs = getattr(split, name)
        for pair in pairs:
            if not dry_run:
                shutil.copy2(pair.image_path, img_dir / pair.image_path.name)
                if pair.label_path and pair.label_path.exists():
                    shutil.copy2(pair.label_path, lbl_dir / pair.label_path.name)
        counts[name] = len(pairs)
    return counts
