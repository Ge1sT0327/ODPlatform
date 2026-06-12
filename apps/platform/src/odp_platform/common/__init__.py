"""common（基础设施层）—— 全平台地基，全员复用。

职责：路径解析、统一日志、字符串/表格格式化、设备信息、
      性能计时、跨任务工具（模型/数据集路径解析、结果指标等）。

主责角色：架构师 / 技术负责人
里程碑：M0（架构基线）+ M1（工程地基）
"""

from odp_platform.common.paths import (
    ROOT_DIR,
    APP_DIR,
    DATA_DIR,
    MODELS_DIR,
    RUNS_DIR,
    PRETRAINED_MODELS_DIR,
    CHECKPOINTS_DIR,
    RAW_DATA_DIR,
    TRAIN_DIR,
    VAL_DIR,
    TEST_DIR,
    CONFIGS_DIR,
    LOGGING_DIR,
    get_dirs_to_initialize,
)
from odp_platform.common.logging_utils import get_logger, log_device_info
from odp_platform.common.string_utils import format_table_row, format_table_separator
from odp_platform.common.performance_utils import time_it

__all__ = [
    # 路径常量
    "ROOT_DIR", "APP_DIR", "DATA_DIR", "MODELS_DIR", "RUNS_DIR",
    "PRETRAINED_MODELS_DIR", "CHECKPOINTS_DIR",
    "RAW_DATA_DIR", "TRAIN_DIR", "VAL_DIR", "TEST_DIR",
    "CONFIGS_DIR", "LOGGING_DIR",
    "get_dirs_to_initialize",
    # 日志
    "get_logger", "log_device_info",
    # 字符串
    "format_table_row", "format_table_separator",
    # 性能
    "time_it",
]
