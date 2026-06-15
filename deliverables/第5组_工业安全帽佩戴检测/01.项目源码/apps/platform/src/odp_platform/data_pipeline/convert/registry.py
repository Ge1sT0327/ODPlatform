"""转换器注册表。以装饰器注册，开闭原则——新增格式不改框架。"""

from dataclasses import dataclass, field
from typing import Dict, Callable, List, Optional
from pathlib import Path

@dataclass
class ConvertOptions:
    """转换选项。
    source_dir: 原始数据集目录
    target_dir: 输出 YOLO 标注目录（不包含 images/labels 后缀）
    format: 源格式名，如 "pascal_voc", "coco", "yolo"
    class_names: 类别名列表（可选，VOC 从 XML 推断，COCO 从 JSON 读取）
    """
    source_dir: Path
    target_dir: Path
    format: str
    class_names: Optional[List[str]] = None

@dataclass
class ConvertResult:
    """转换结果。"""
    success: bool
    error: Optional[str] = None
    total_images: int = 0
    total_labels: int = 0  # 成功转换的标注文件数
    class_counts: Dict[str, int] = field(default_factory=dict)  # {class_name: count}

# 全局注册表
_REGISTRY: Dict[str, Callable] = {}

def register(name: str):
    """装饰器: @register("pascal_voc") 注册一个转换器函数。
    被装饰函数签名: (ConvertOptions) -> ConvertResult
    """
    def decorator(func: Callable):
        _REGISTRY[name] = func
        return func
    return decorator

def list_capabilities() -> Dict[str, str]:
    """返回 {格式名: 转换器函数名}。"""
    return {k: v.__name__ for k, v in _REGISTRY.items()}

def get_converter(name: str) -> Callable:
    """按名获取转换器函数。未注册则 raise KeyError。"""
    if name not in _REGISTRY:
        raise KeyError(f"未注册的转换器: '{name}'。可用: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]
