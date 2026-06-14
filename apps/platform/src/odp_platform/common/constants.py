"""平台级常量：任务类型、默认值、验证阈值、退出码。"""
from enum import Enum

class TaskType(str, Enum):
    DETECT = "detect"
    SEGMENT = "segment"

class ExitCode:
    SUCCESS = 0
    USER_ERROR = 1
    SYSTEM_ERROR = 2

class ValidationExitCode:
    PASS = 0
    WARNING = 1
    ERROR = 2

# 默认值
DEFAULT_DATASET = "safety_helmet"
DEFAULT_CONFIG = "train"
DEFAULT_MODEL = "yolov8n.pt"
DEFAULT_TASK = TaskType.DETECT

# 数据验证阈值
PAIR_MISSING_INFO_THRESHOLD = 0.01    # <1% → INFO
PAIR_MISSING_WARN_THRESHOLD = 0.05    # 1%~5% → WARNING, >5% → ERROR

# 文件扩展名（不依赖 frame_source 时 common 自己也有）
IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"})
LABEL_EXTENSION = ".txt"
