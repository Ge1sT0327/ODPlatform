"""检查注册表。装饰器 @check 自动注册。"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Callable, List, Optional, Any
from pathlib import Path

class CheckSeverity(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

    def __ge__(self, other):
        order = {CheckSeverity.INFO: 0, CheckSeverity.WARNING: 1, CheckSeverity.ERROR: 2}
        return order[self] >= order[other]

@dataclass
class CheckResult:
    """
    单项检查结果。
    severity: 严重程度
    message: 人类可读的摘要
    details: 结构化详情（计数、示例路径等）
    passed: 派生属性，severity != ERROR 即为 True
    """
    check_name: str
    severity: CheckSeverity
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def passed(self) -> bool:
        return self.severity != CheckSeverity.ERROR

@dataclass
class CheckContext:
    """传给检查函数的上下文。"""
    yaml_path: Path                     # data.yaml 的路径
    dataset_name: str
    task_type: str = "detect"
    snapshot: Optional[Any] = None      # DatasetSnapshot 实例

_REGISTRY: Dict[str, Callable] = {}

def check(name: str):
    """装饰器: @check("yaml_schema") 注册检查函数。
    函数签名: (CheckContext) -> CheckResult
    """
    def decorator(func: Callable):
        _REGISTRY[name] = func
        return func
    return decorator

def get_check(name: str) -> Callable:
    if name not in _REGISTRY:
        raise KeyError(f"未注册的检查: '{name}'。可用: {list(_REGISTRY.keys())}")
    return _REGISTRY[name]

def get_all_checks() -> Dict[str, Callable]:
    return dict(_REGISTRY)

def list_check_names() -> List[str]:
    return list(_REGISTRY.keys())
