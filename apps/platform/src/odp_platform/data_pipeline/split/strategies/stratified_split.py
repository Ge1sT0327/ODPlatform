"""分层切分策略：按类别比例保持均衡。"""

import random
from collections import defaultdict
from odp_platform.data_pipeline.split.strategy_registry import register_strategy, SplitOptions
from odp_platform.data_pipeline.split.manifest import SplitManifest, ImageLabelPair

@register_strategy("stratified")
def stratified_split(manifest: SplitManifest, options: SplitOptions) -> dict:
    """
    按每张图片的主类别进行分层，确保 train/val/test 类别比例一致。
    """
    # 按类别分组
    by_class = defaultdict(list)
    for pair in manifest.pairs:
        if pair.label_path and pair.label_path.exists():
            # 读第一行的类别 id 作为主类别
            first_line = pair.label_path.read_text(encoding="utf-8").strip().split("\n")[0]
            cls_id = int(first_line.split()[0])
        else:
            cls_id = -1  # 无标注
        by_class[cls_id].append(pair)

    rng = random.Random(options.seed)
    train, val, test = [], [], []
    for cls_id, pairs in by_class.items():
        rng.shuffle(pairs)
        n = len(pairs)
        train_end = max(1, round(n * options.ratios[0]))
        val_end = train_end + max(1, round(n * options.ratios[1]))
        train.extend(pairs[:train_end])
        val.extend(pairs[train_end:val_end])
        test.extend(pairs[val_end:])

    return {"train": train, "val": val, "test": test}
