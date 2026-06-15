"""切分清单：扫描图片-标注对，生成 SplitManifest。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List
from odp_platform.common.constants import IMAGE_EXTENSIONS

@dataclass
class ImageLabelPair:
    image_path: Path
    label_path: Path

@dataclass
class SplitManifest:
    pairs: List[ImageLabelPair] = field(default_factory=list)
    total: int = 0
    class_distribution: dict = field(default_factory=dict)  # {class_id: count}

    @classmethod
    def from_directory(cls, images_dir: Path, labels_dir: Path) -> "SplitManifest":
        """
        扫描 images_dir 下所有图片文件，找到对应的 labels_dir/<stem>.txt。
        确保每个图片有对应标注（缺失时 label_path 为 None，但不报错——由 data_validation 负责检查）。
        """
        pairs = []
        for img_path in sorted(images_dir.iterdir()):
            if img_path.suffix.lower() not in IMAGE_EXTENSIONS:
                continue
            label_path = labels_dir / f"{img_path.stem}.txt"
            pairs.append(ImageLabelPair(
                image_path=img_path,
                label_path=label_path if label_path.exists() else None,
            ))
        return cls(pairs=pairs, total=len(pairs))
