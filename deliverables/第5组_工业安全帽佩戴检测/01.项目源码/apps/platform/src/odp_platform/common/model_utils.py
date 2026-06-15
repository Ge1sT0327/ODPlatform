"""跨任务工具：模型/数据集路径解析、日志重命名。"""

from pathlib import Path
from typing import Optional, List
from odp_platform.common.paths import (
    CHECKPOINTS_DIR, PRETRAINED_MODELS_DIR, DATASET_CONFIGS_DIR,
)

def resolve_model_path(
    model: str,
    search_dirs: Optional[List[Path]] = None,
) -> Path:
    """
    将模型名/路径解析为真实文件路径。
    搜索顺序:
    1. 若 model 是绝对路径且存在 → 直接返回
    2. 若 model 是相对于 CWD 的路径且存在 → 直接返回
    3. 在搜索目录列表中依次查找 model 文件名
    默认搜索目录: CHECKPOINTS_DIR, PRETRAINED_MODELS_DIR
    """
    p = Path(model)
    if p.is_absolute() and p.exists():
        return p
    cwd_path = Path.cwd() / model
    if cwd_path.exists():
        return cwd_path.resolve()

    dirs = search_dirs or [CHECKPOINTS_DIR, PRETRAINED_MODELS_DIR]
    for d in dirs:
        candidate = d / model
        if candidate.exists():
            return candidate
        # 也尝试按文件名匹配
        if d.exists():
            for f in d.glob("*.pt"):
                if f.name == model or f.stem == model:
                    return f

    # 兼容 ultralytics 官方预训练权重（如 yolov8n.pt）：本地不存在时由 ultralytics 自动下载
    if model.lower().startswith("yolo") and model.endswith(".pt"):
        return Path(model)

    raise FileNotFoundError(f"找不到模型: '{model}'。搜索目录: {[str(d) for d in dirs]}")

def resolve_dataset_path(data: str) -> Path:
    """
    将数据集 yaml 名称解析为真实路径。
    若 data 已是路径 → 直接返回。
    否则在 DATASET_CONFIGS_DIR 中查找 <data>.yaml。
    """
    p = Path(data)
    if p.exists():
        return p.resolve()
    candidate = DATASET_CONFIGS_DIR / f"{data}.yaml" if not data.endswith(".yaml") else DATASET_CONFIGS_DIR / data
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"找不到数据集配置: '{data}'。搜索: {DATASET_CONFIGS_DIR}")

def rename_log_to_save_dir(log_name: str, save_dir: Path) -> None:
    """将日志文件名与底层框架 run 产出目录对齐（便于日志↔结果互查）。"""
    import logging
    logger = logging.getLogger(f"odp_platform.{log_name}")
    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler):
            old_path = Path(handler.baseFilename)
            new_path = save_dir / old_path.name
            handler.close()
            logger.removeHandler(handler)
            old_path.rename(new_path)
            new_handler = logging.FileHandler(new_path, encoding="utf-8")
            new_handler.setLevel(handler.level)
            new_handler.setFormatter(handler.formatter)
            logger.addHandler(new_handler)
