"""runtime_config 子系统对外公共 API。"""

from odp_platform.runtime_config.base_config import BaseConfig, ConfigSource
from odp_platform.runtime_config.train_config import YOLOTrainConfig
from odp_platform.runtime_config.val_config import YOLOValConfig
from odp_platform.runtime_config.infer_config import YOLOInferConfig
from odp_platform.runtime_config.loader import load_yaml_config, apply_cli_overrides
from odp_platform.runtime_config.merger import ConfigMerger
from odp_platform.runtime_config.generator import ConfigGenerator

def build_train_config(
    yaml_path: str = None,
    cli_overrides: dict = None,
) -> YOLOTrainConfig:
    """构建训练配置: DEFAULT → YAML → CLI。"""
    merger = ConfigMerger()
    yaml_dict = load_yaml_config(yaml_path) if yaml_path else {}
    cli_dict = cli_overrides or {}
    config, _ = merger.merge(YOLOTrainConfig, yaml_dict, cli_dict)
    return config

def build_val_config(
    yaml_path: str = None,
    cli_overrides: dict = None,
) -> YOLOValConfig:
    merger = ConfigMerger()
    yaml_dict = load_yaml_config(yaml_path) if yaml_path else {}
    cli_dict = cli_overrides or {}
    config, _ = merger.merge(YOLOValConfig, yaml_dict, cli_dict)
    return config

def build_infer_config(
    yaml_path: str = None,
    cli_overrides: dict = None,
):
    merger = ConfigMerger()
    yaml_dict = load_yaml_config(yaml_path) if yaml_path else {}
    cli_dict = cli_overrides or {}
    return merger.merge(YOLOInferConfig, yaml_dict, cli_dict)

__all__ = [
    "BaseConfig", "ConfigSource",
    "YOLOTrainConfig", "YOLOValConfig", "YOLOInferConfig",
    "build_train_config", "build_val_config", "build_infer_config",
    "load_yaml_config", "apply_cli_overrides",
    "ConfigMerger", "ConfigGenerator",
]
