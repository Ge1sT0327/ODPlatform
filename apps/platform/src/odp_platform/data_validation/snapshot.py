"""数据集快照：一次扫盘，各检查复用。"""

from dataclasses import dataclass, field
from typing import Dict, List, Set
from pathlib import Path
from odp_platform.common.paths import (
    TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR,
    VAL_IMAGES_DIR, VAL_LABELS_DIR,
    TEST_IMAGES_DIR, TEST_LABELS_DIR,
)
from odp_platform.common.constants import IMAGE_EXTENSIONS

@dataclass
class SplitSnapshot:
    name: str
    images_dir: Path
    labels_dir: Path
    image_files: Set[str] = field(default_factory=set)
    label_files: Set[str] = field(default_factory=set)
    class_ids: Set[int] = field(default_factory=set)
    total_labels: int = 0

@dataclass
class DatasetSnapshot:
    dataset_name: str
    splits: Dict[str, SplitSnapshot] = field(default_factory=dict)
    nc: int = 0
    class_names: List[str] = field(default_factory=list)

def build_snapshot(yaml_path: Path, dataset_name: str) -> DatasetSnapshot:
    """
    遍历 data/{train,val,test}/images/ 和 labels/。
    收集: 图片文件名集合、标注文件名集合、类别 id 集合、标注行数。
    """
    import yaml
    config = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    nc = config.get("nc", 0)
    class_names = [config["names"].get(i, str(i)) for i in range(nc)] if "names" in config else []

    snapshot = DatasetSnapshot(dataset_name=dataset_name, nc=nc, class_names=class_names)
    split_configs = [
        ("train", TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR),
        ("val", VAL_IMAGES_DIR, VAL_LABELS_DIR),
        ("test", TEST_IMAGES_DIR, TEST_LABELS_DIR),
    ]

    for name, img_dir, lbl_dir in split_configs:
        ss = SplitSnapshot(name=name, images_dir=img_dir, labels_dir=lbl_dir)
        if img_dir.exists():
            ss.image_files = {
                f.stem for f in img_dir.iterdir()
                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS
            }
        if lbl_dir.exists():
            for lf in lbl_dir.glob("*.txt"):
                ss.label_files.add(lf.stem)
                for line in lf.read_text(encoding="utf-8").strip().split("\n"):
                    if not line.strip():
                        continue
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        ss.class_ids.add(int(parts[0]))
                        ss.total_labels += 1
        snapshot.splits[name] = ss

    return snapshot
