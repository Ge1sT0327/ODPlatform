"""切分执行器。"""

from dataclasses import dataclass
from typing import List
from odp_platform.data_pipeline.split.manifest import SplitManifest, ImageLabelPair
from odp_platform.data_pipeline.split.strategy_registry import (
    SplitOptions, get_strategy,
)
import odp_platform.data_pipeline.split.strategies  # noqa

@dataclass
class SplitResult:
    train: List[ImageLabelPair]
    val: List[ImageLabelPair]
    test: List[ImageLabelPair]

    @property
    def total(self) -> int:
        return len(self.train) + len(self.val) + len(self.test)

def split_pairs(manifest: SplitManifest, options: SplitOptions = None) -> SplitResult:
    """按策略和比例执行切分。"""
    if options is None:
        options = SplitOptions()
    strategy = get_strategy(options.strategy)
    result = strategy(manifest, options)
    return SplitResult(
        train=result["train"],
        val=result["val"],
        test=result["test"],
    )
