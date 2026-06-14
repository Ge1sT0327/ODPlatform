"""生效配置日志：配合 runtime_config 打印三源溯源。"""

import logging
from typing import Optional
from odp_platform.runtime_config.base_config import BaseConfig

def log_effective_config(
    config: BaseConfig,
    logger: Optional[logging.Logger] = None,
) -> None:
    """将配置对象以结构化格式输出到 logger。"""
    log = logger or logging.getLogger("odp_platform.config")
    log.info("=" * 50)
    log.info(f"生效配置: {config.__class__.__name__}")
    for group, fields in config.get_field_groups().items():
        log.info(f"  [{group}]")
        for fname in fields:
            source = config._source_map.get(fname, "default")
            value = getattr(config, fname, "<N/A>")
            log.info(f"    {fname} = {value!r}  (来源: {source})")
    log.info("=" * 50)
