"""三源合并引擎：DEFAULT → YAML → CLI，带来源溯源。"""

from typing import Dict, Tuple, Type
from odp_platform.runtime_config.base_config import BaseConfig, ConfigSource

class ConfigMerger:
    """
    三源合并。
    - 先从配置类的 default 值构建实例
    - 再用 YAML 值覆盖（记录来源 YAML）
    - 最后用 CLI 值覆盖（记录来源 CLI）
    """

    def merge(
        self,
        config_cls: Type[BaseConfig],
        yaml_dict: dict,
        cli_dict: dict,
    ) -> Tuple[BaseConfig, Dict[str, ConfigSource]]:
        # Step 1: 从 default 构建
        defaults = {}
        for name, field in config_cls.model_fields.items():
            if field.default is not ...:
                defaults[name] = field.default

        # Step 2: 合并 YAML（只取 config_cls 已知的字段）
        merged = dict(defaults)
        source_map = {k: ConfigSource.DEFAULT for k in merged}
        for k, v in yaml_dict.items():
            if k in config_cls.model_fields:
                merged[k] = v
                source_map[k] = ConfigSource.YAML

        # Step 3: 合并 CLI
        for k, v in cli_dict.items():
            if k in config_cls.model_fields and v is not None:
                merged[k] = v
                source_map[k] = ConfigSource.CLI

        # Step 4: 构建 Pydantic 实例（触发校验）
        config = config_cls(**merged)
        config._source_map = source_map
        return config, source_map

    def get_source(self, field_name: str, source_map: dict) -> ConfigSource:
        return source_map.get(field_name, ConfigSource.DEFAULT)

    def print_source_trace(self, config: BaseConfig) -> str:
        """生成可读的来源溯源表。"""
        lines = ["配置来源溯源:", "-" * 50]
        for name in config.model_fields.keys():
            source = config._source_map.get(name, ConfigSource.DEFAULT)
            value = getattr(config, name, "<N/A>")
            lines.append(f"  {name}: {value!r}  ← {source.value}")
        return "\n".join(lines)
