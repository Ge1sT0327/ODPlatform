"""切分策略公共工具。"""

from typing import List
from odp_platform.data_pipeline.split.manifest import ImageLabelPair

def apply_ratios(pairs: List[ImageLabelPair], ratios: List[float]) -> tuple:
    """
    按 ratios (如 [0.8, 0.1, 0.1]) 将 pairs 切为三段。
    返回 (train_pairs, val_pairs, test_pairs)，保证不重不漏。
    """
    n = len(pairs)
    train_end = max(1, round(n * ratios[0]))
    val_end = train_end + max(1, round(n * ratios[1]))
    return (
        pairs[:train_end],
        pairs[train_end:val_end],
        pairs[val_end:],
    )
