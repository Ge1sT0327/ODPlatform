"""数据流水线编排器：串联"转换→切分→物化→写 yaml"。"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from odp_platform.data_pipeline.convert.registry import ConvertOptions, ConvertResult
from odp_platform.data_pipeline.convert.service import convert_data_to_yolo
from odp_platform.data_pipeline.split.manifest import SplitManifest
from odp_platform.data_pipeline.split.splitter import split_pairs, SplitResult
from odp_platform.data_pipeline.split.strategy_registry import SplitOptions
from odp_platform.data_pipeline.split.materializer import materialize_split
from odp_platform.data_pipeline.split.yaml_writer import write_dataset_yaml
from odp_platform.common.paths import raw_dataset_root, TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR

@dataclass
class PipelineResult:
    success: bool
    error: Optional[str] = None
    convert: Optional[ConvertResult] = None
    split: Optional[SplitResult] = None
    dataset_yaml_path: Optional[Path] = None

class DatasetPipeline:
    def __init__(self):
        self.result = PipelineResult(success=False)

    def run(
        self,
        dataset_name: str,
        source_format: str,
        class_names: list = None,
        split_ratios: list = None,
        split_strategy: str = "random",
        seed: int = 42,
    ) -> PipelineResult:
        """
        完整数据流水线。

        1. Convert: raw/<dataset>/ → 临时位置 (TRAIN_LABELS_DIR 作为中转)
        2. Split: 扫描转换后的标注 + 原始图片 → 切分
        3. Materialize: 物化到 data/{train,val,test}/
        4. YAML: 写 configs/datasets/<dataset>.yaml
        """
        try:
            src_dir = raw_dataset_root(dataset_name)
            if not src_dir.exists():
                return PipelineResult(success=False, error=f"原始数据目录不存在: {src_dir}")

            # Step 1: Convert
            convert_opt = ConvertOptions(
                source_dir=src_dir,
                target_dir=TRAIN_LABELS_DIR.parent / "_tmp_convert",
                format=source_format,
                class_names=class_names,
            )
            conv_result = convert_data_to_yolo(convert_opt)
            if not conv_result.success:
                return PipelineResult(success=False, error=conv_result.error, convert=conv_result)

            # Step 2: Build manifest from source images
            img_dir = src_dir
            if not any(img_dir.glob("*.jpg")) and not any(img_dir.glob("*.png")):
                # 尝试 JPEGImages/ 子目录（VOC 习惯）
                candidate = src_dir / "JPEGImages"
                if candidate.exists():
                    img_dir = candidate

            labels_dir = convert_opt.target_dir / "labels"
            if not labels_dir.exists():
                labels_dir = TRAIN_LABELS_DIR  # fallback

            manifest = SplitManifest.from_directory(img_dir, labels_dir)
            if manifest.total == 0:
                return PipelineResult(success=False, error="未找到任何图片文件")

            # Step 3: Split
            ratios = split_ratios or [0.8, 0.1, 0.1]
            split_opt = SplitOptions(ratios=ratios, strategy=split_strategy, seed=seed)
            split_result = split_pairs(manifest, split_opt)

            # Step 4: Materialize
            materialize_split(split_result)

            # Step 5: Write data.yaml
            effective_class_names = class_names
            if not effective_class_names and conv_result.class_counts:
                effective_class_names = list(conv_result.class_counts.keys())
            if not effective_class_names:
                effective_class_names = ["unknown"]
            yaml_path = write_dataset_yaml(dataset_name, effective_class_names)

            self.result = PipelineResult(
                success=True,
                convert=conv_result,
                split=split_result,
                dataset_yaml_path=yaml_path,
            )
            return self.result
        except Exception as e:
            return PipelineResult(success=False, error=str(e))
