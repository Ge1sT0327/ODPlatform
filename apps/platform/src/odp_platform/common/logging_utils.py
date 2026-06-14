import io
import logging
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# ---- 着色支持 (cross-platform) ----
def _supports_color() -> bool:
    """检测终端是否支持 ANSI 着色（Windows 10+ 支持）。"""
    ...

def _safe_stdout_stream():
    """返回一个使用 UTF-8（错误替换）的 stdout 包装，避免中文/emoji 输出崩溃。"""
    try:
        return io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        return sys.stdout

LEVEL_COLORS = {
    logging.DEBUG:    "\033[36m",  # cyan
    logging.INFO:     "\033[32m",  # green
    logging.WARNING:  "\033[33m",  # yellow
    logging.ERROR:    "\033[31m",  # red
    logging.CRITICAL: "\033[35m",  # magenta
}
RESET = "\033[0m"

class _ColoredFormatter(logging.Formatter):
    """按级别着色，格式: 2026-06-14 10:30:00 [INFO   ] [module] message"""
    def format(self, record: logging.LogRecord) -> str:
        color = LEVEL_COLORS.get(record.levelno, "")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = f"{record.levelname:<7}"
        msg = super().format(record)
        return f"{color}{timestamp} [{level}] [{record.name}] {msg}{RESET}"

_LOGGERS: dict = {}  # 缓存已创建的 logger

def get_logger(
    name: str,
    log_type: str = "default",
    log_dir: Optional[Path] = None,
    level: int = logging.DEBUG,
) -> logging.Logger:
    """
    获取/创建命名 logger，挂载于 'odp_platform' 命名空间下。
    自动添加 console handler（着色）和 file handler（无着色）。

    Args:
        name: 模块名，如 "training"、"data_validation"
        log_type: 日志子目录名，如 "train"、"validate"
        log_dir: file handler 输出目录，默认 LOGGING_DIR / log_type
        level: 日志级别，默认 DEBUG

    Returns:
        logging.Logger 实例

    console handler: 级别=INFO，着色格式
    file handler: 级别=DEBUG，文件名 {name}_{timestamp}.log
    """
    full_name = f"odp_platform.{name}"
    if full_name in _LOGGERS:
        return _LOGGERS[full_name]

    logger = logging.getLogger(full_name)
    logger.setLevel(level)
    logger.propagate = False  # 不向根 logger 冒泡

    # console handler
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        ch = logging.StreamHandler(_safe_stdout_stream())
        ch.setLevel(logging.INFO)
        ch.setFormatter(_ColoredFormatter("%(message)s"))
        logger.addHandler(ch)

    # file handler
    if log_dir is None:
        from odp_platform.common.paths import LOGGING_DIR
        log_dir = LOGGING_DIR / log_type
    log_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
    fh = logging.FileHandler(log_dir / f"{name}_{ts}.log", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)-7s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)

    _LOGGERS[full_name] = logger
    return logger

def log_device_info(target_logger: Optional[logging.Logger] = None) -> dict:
    """
    记录当前设备信息（CPU/GPU/OS）到指定 logger 或 root logger。
    返回结构化设备信息 dict: {"platform": str, "cpu_count": int, "gpus": [...]}
    torch 不可用时 GPU 列表为空。
    """
    import platform
    info = {"platform": platform.platform(), "cpu_count": os.cpu_count(), "gpus": []}
    try:
        import torch
        info["gpus"] = [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())]
        info["cuda_available"] = torch.cuda.is_available()
    except ImportError:
        info["cuda_available"] = False
    log = target_logger or logging.getLogger("odp_platform")
    log.info(f"设备信息: {info}")
    return info
