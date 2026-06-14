"""YAML 加载器 + CLI 覆盖器，fail-fast 校验。"""

from pathlib import Path
from typing import Dict, Any
import yaml

def load_yaml_config(path: str | Path) -> Dict[str, Any]:
    """
    加载一个 YAML 配置文件。
    文件不存在时返回空 dict。
    YAML 语法错误时 raise ValueError 并给出路径。
    """
    path = Path(path)
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data if data else {}
    except yaml.YAMLError as e:
        raise ValueError(f"YAML 解析失败 [{path}]: {e}") from e

def apply_cli_overrides(base: Dict[str, Any], cli_args: Dict[str, Any]) -> Dict[str, Any]:
    """
    将 CLI 参数覆盖到 base dict 上。
    仅覆盖 cli_args 中值非 None 的键。
    """
    result = dict(base)
    for k, v in cli_args.items():
        if v is not None:
            result[k] = v
    return result
