"""随机切分策略。"""

import random
from odp_platform.data_pipeline.split.strategy_registry import register_strategy, SplitOptions
from odp_platform.data_pipeline.split.manifest import SplitManifest
from odp_platform.data_pipeline.split.strategies._common import apply_ratios

@register_strategy("random")
def random_split(manifest: SplitManifest, options: SplitOptions) -> dict:
    """打乱后按比例切分。"""
    pairs = list(manifest.pairs)
    rng = random.Random(options.seed)
    rng.shuffle(pairs)
    train, val, test = apply_ratios(pairs, options.ratios)
    return {"train": train, "val": val, "test": test}
