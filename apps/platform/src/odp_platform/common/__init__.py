"""common 基础设施层对外公共 API。"""

from odp_platform.common.paths import (
    ROOT_DIR, APP_DIR,
    DATA_DIR, MODELS_DIR, RUNS_DIR,
    PRETRAINED_MODELS_DIR, CHECKPOINTS_DIR,
    RAW_DATA_DIR,
    TRAIN_DIR, VAL_DIR, TEST_DIR,
    TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR,
    VAL_IMAGES_DIR, VAL_LABELS_DIR,
    TEST_IMAGES_DIR, TEST_LABELS_DIR,
    CONFIGS_DIR, DATASET_CONFIGS_DIR, RUNTIME_CONFIGS_DIR,
    LOGGING_DIR, UNIT_TEST_DIR, DOCS_DIR, SCRIPTS_DIR,
    META_DIR, META_LOGGING_DIR,
    VALIDATION_RUNS_DIR,
    get_dirs_to_initialize, get_dirs_to_reset, is_protected,
    raw_dataset_root, dataset_yaml_path, runtime_config_path,
    validation_run_dir,
)
from odp_platform.common.logging_utils import get_logger, log_device_info
from odp_platform.common.string_utils import (
    display_width, pad_to_width, format_table_row, format_table_separator,
)
from odp_platform.common.system_utils import get_system_info
from odp_platform.common.performance_utils import time_it
from odp_platform.common.constants import (
    TaskType, ExitCode, ValidationExitCode,
    DEFAULT_DATASET, DEFAULT_CONFIG, DEFAULT_MODEL, DEFAULT_TASK,
    PAIR_MISSING_INFO_THRESHOLD, PAIR_MISSING_WARN_THRESHOLD,
    IMAGE_EXTENSIONS, LABEL_EXTENSION,
)

__all__ = [
    # paths
    "ROOT_DIR", "APP_DIR", "DATA_DIR", "MODELS_DIR", "RUNS_DIR",
    "PRETRAINED_MODELS_DIR", "CHECKPOINTS_DIR", "RAW_DATA_DIR",
    "TRAIN_DIR", "VAL_DIR", "TEST_DIR",
    "TRAIN_IMAGES_DIR", "TRAIN_LABELS_DIR",
    "VAL_IMAGES_DIR", "VAL_LABELS_DIR",
    "TEST_IMAGES_DIR", "TEST_LABELS_DIR",
    "CONFIGS_DIR", "DATASET_CONFIGS_DIR", "RUNTIME_CONFIGS_DIR",
    "LOGGING_DIR", "UNIT_TEST_DIR", "DOCS_DIR", "SCRIPTS_DIR",
    "META_DIR", "META_LOGGING_DIR", "VALIDATION_RUNS_DIR",
    "get_dirs_to_initialize", "get_dirs_to_reset", "is_protected",
    "raw_dataset_root", "dataset_yaml_path", "runtime_config_path",
    "validation_run_dir",
    # logging
    "get_logger", "log_device_info",
    # string
    "display_width", "pad_to_width", "format_table_row", "format_table_separator",
    # system
    "get_system_info",
    # performance
    "time_it",
    # constants
    "TaskType", "ExitCode", "ValidationExitCode",
    "DEFAULT_DATASET", "DEFAULT_CONFIG", "DEFAULT_MODEL", "DEFAULT_TASK",
    "PAIR_MISSING_INFO_THRESHOLD", "PAIR_MISSING_WARN_THRESHOLD",
    "IMAGE_EXTENSIONS", "LABEL_EXTENSION",
]
