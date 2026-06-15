"""反射式配置模板生成器 + odp-gen-config CLI 入口。"""

import sys
from pathlib import Path
from typing import Type
from odp_platform.runtime_config.base_config import BaseConfig
from odp_platform.runtime_config.train_config import YOLOTrainConfig
from odp_platform.runtime_config.val_config import YOLOValConfig
from odp_platform.runtime_config.infer_config import YOLOInferConfig
from odp_platform.common.paths import runtime_config_path
from odp_platform.common.constants import ExitCode

CONFIG_CLASSES: dict = {
    "train": YOLOTrainConfig,
    "val": YOLOValConfig,
    "infer": YOLOInferConfig,
}

class ConfigGenerator:
    """由 Pydantic 模型结构自动生成带注释的 YAML 模板。"""

    @staticmethod
    def generate(config_type: str) -> str:
        """
        返回 YAML 文本。
        按字段分组生成注释头 + 键值对 + 行内说明。
        """
        config_cls = CONFIG_CLASSES.get(config_type)
        if config_cls is None:
            raise ValueError(f"未知配置类型: '{config_type}'。可选: {list(CONFIG_CLASSES.keys())}")
        return ConfigGenerator._gen(config_cls)

    @staticmethod
    def _gen(config_cls: Type[BaseConfig]) -> str:
        groups = config_cls.get_field_groups()
        lines = [
            f"# ============================================================",
            f"# ODPlatform {config_cls.__name__} 配置模板",
            f"# 修改此文件后运行对应命令即可生效",
            f"# ============================================================",
            f"",
        ]
        for group_name, field_names in groups.items():
            lines.append(f"# --- {group_name} ---")
            for fname in field_names:
                meta = config_cls.get_field_metadata(fname)
                desc = meta.get("description", "")
                example = meta.get("example", "")
                default_val = meta.get("default", ...)
                hints = []
                if desc:
                    hints.append(desc)
                if example:
                    hints.append(f"示例: {example}")
                comment = "  # " + " | ".join(hints) if hints else ""
                # 格式化默认值
                val = default_val
                if isinstance(val, str):
                    val = f'"{val}"'
                lines.append(f"{fname}: {val}{comment}")
            lines.append("")
        return "\n".join(lines)

def main(argv: list = None) -> int:
    """odp-gen-config CLI 入口。"""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print(f"用法: odp-gen-config <train|val|infer>")
        return ExitCode.USER_ERROR

    config_type = argv[0]
    if config_type not in CONFIG_CLASSES:
        print(f"未知配置类型: '{config_type}'。可选: {list(CONFIG_CLASSES.keys())}")
        return ExitCode.USER_ERROR

    try:
        yaml_text = ConfigGenerator.generate(config_type)
        out = runtime_config_path(config_type)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(yaml_text, encoding="utf-8")
        print(f"配置模板已生成: {out}")
        return ExitCode.SUCCESS
    except Exception as e:
        print(f"生成失败: {e}", file=sys.stderr)
        return ExitCode.SYSTEM_ERROR

if __name__ == "__main__":
    sys.exit(main())
