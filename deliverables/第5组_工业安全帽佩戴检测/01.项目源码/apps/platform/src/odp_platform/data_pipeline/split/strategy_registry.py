"""切分策略注册表。"""

from dataclasses import dataclass, field
from typing import Dict, Callable, List

@dataclass
class SplitOptions:
    ratios: List[float] = field(default_factory=lambda: [0.8, 0.1, 0.1])  # train/val/test
    strategy: str = "random"
    seed: int = 42

_REGISTRY: Dict[str, Callable] = {}

def register_strategy(name: str):
    """装饰器: @register_strategy("random") 注册切分策略。
    函数签名: (manifest: SplitManifest, options: SplitOptions) -> dict
    返回: {"train": [ImageLabelPair, ...], "val": [...], "test": [...]}
    """
    def decorator(func):
        _REGISTRY[name] = func
        return func
    return decorator

def list_strategies() -> List[str]:
    return list(_REGISTRY.keys())

def get_strategy(name: str) -> Callable:
    if name not in _REGISTRY:
        raise KeyError(f"未注册的策略: '{name}'。可用: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]
