from pathlib import Path
from typing import List, Tuple

# ---- marker file 定位 ----
WORKSPACE_MARKER: str = ".odp-workspace"

def _find_workspace_root(start: Path, markers: Tuple[str, ...] = (WORKSPACE_MARKER,)) -> Path:
    """
    从 start 向上遍历父目录，返回第一个包含 marker 文件的目录。
    start 是文件时取其 parent 开始。
    若遍历到文件系统根仍未找到，抛出 FileNotFoundError。
    """
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for parent in [current, *current.parents]:
        for marker in markers:
            if (parent / marker).exists():
                return parent
    raise FileNotFoundError(
        f"找不到 workspace marker ({markers})。请确认仓库根存在 {WORKSPACE_MARKER} 文件。"
    )

ROOT_DIR: Path = _find_workspace_root(Path(__file__))

# ---- 端根目录 ----
APP_DIR: Path = ROOT_DIR / "apps" / "platform"

# ---- 共享资产（ROOT_DIR 下）----
DATA_DIR: Path = ROOT_DIR / "data"
MODELS_DIR: Path = ROOT_DIR / "models"
RUNS_DIR: Path = ROOT_DIR / "runs"
PRETRAINED_MODELS_DIR: Path = MODELS_DIR / "pretrained"
CHECKPOINTS_DIR: Path = MODELS_DIR / "checkpoints"
RAW_DATA_DIR: Path = DATA_DIR / "raw"
TRAIN_DIR: Path = DATA_DIR / "train"
VAL_DIR: Path = DATA_DIR / "val"
TEST_DIR: Path = DATA_DIR / "test"
TRAIN_IMAGES_DIR: Path = TRAIN_DIR / "images"
TRAIN_LABELS_DIR: Path = TRAIN_DIR / "labels"
VAL_IMAGES_DIR: Path = VAL_DIR / "images"
VAL_LABELS_DIR: Path = VAL_DIR / "labels"
TEST_IMAGES_DIR: Path = TEST_DIR / "images"
TEST_LABELS_DIR: Path = TEST_DIR / "labels"

# ---- 端私有资产（APP_DIR 下）----
CONFIGS_DIR: Path = APP_DIR / "configs"
LOGGING_DIR: Path = APP_DIR / "logging"
UNIT_TEST_DIR: Path = APP_DIR / "tests"
DATASET_CONFIGS_DIR: Path = CONFIGS_DIR / "datasets"
RUNTIME_CONFIGS_DIR: Path = CONFIGS_DIR / "runtime"

# ---- 文档 & 工程 ----
DOCS_DIR: Path = ROOT_DIR / "docs"
SCRIPTS_DIR: Path = ROOT_DIR / "scripts"

# ---- 元数据 ----
META_DIR: Path = ROOT_DIR / ".odp-meta"
META_LOGGING_DIR: Path = META_DIR / "logs"

# ---- 数据验证运行目录 ----
VALIDATION_RUNS_DIR: Path = RUNS_DIR / "data_validation"

# ---- 路径辅助函数 ----
def raw_dataset_root(dataset_name: str) -> Path:
    """返回原始数据集根目录: data/raw/<dataset_name>/"""
    return RAW_DATA_DIR / dataset_name

def dataset_yaml_path(dataset_name: str) -> Path:
    """返回数据集配置路径: configs/datasets/<dataset_name>.yaml"""
    return DATASET_CONFIGS_DIR / f"{dataset_name}.yaml"

def runtime_config_path(config_name: str) -> Path:
    """返回运行配置路径: configs/runtime/<config_name>.yaml"""
    return RUNTIME_CONFIGS_DIR / f"{config_name}.yaml"

def validation_run_dir(run_id: str) -> Path:
    """返回验证运行产物目录: runs/data_validation/<run_id>/"""
    return VALIDATION_RUNS_DIR / run_id

def get_dirs_to_initialize() -> List[Path]:
    """odp-init 的数据源。返回需要确保存在的所有目录。"""
    return [
        DATA_DIR, RUNS_DIR, MODELS_DIR, PRETRAINED_MODELS_DIR, CHECKPOINTS_DIR,
        RAW_DATA_DIR,
        TRAIN_IMAGES_DIR, TRAIN_LABELS_DIR, VAL_IMAGES_DIR, VAL_LABELS_DIR,
        TEST_IMAGES_DIR, TEST_LABELS_DIR,
        CONFIGS_DIR, DATASET_CONFIGS_DIR, RUNTIME_CONFIGS_DIR,
        LOGGING_DIR, UNIT_TEST_DIR,
        SCRIPTS_DIR, DOCS_DIR, META_LOGGING_DIR,
    ]

def get_dirs_to_reset() -> List[Path]:
    """odp-reset 可安全清理的目录列表。绝不包含 git 跟踪的目录。"""
    return [
        TRAIN_DIR, VAL_DIR, TEST_DIR,
        RUNS_DIR, CHECKPOINTS_DIR,
        LOGGING_DIR, CONFIGS_DIR,
    ]

PROTECTED_DIRS: Tuple[Path, ...] = (
    ROOT_DIR, ROOT_DIR / "apps", ROOT_DIR / "packages",
    APP_DIR, APP_DIR / "src",
    SCRIPTS_DIR, DOCS_DIR, UNIT_TEST_DIR,
    ROOT_DIR / ".git", ROOT_DIR / ".odp-workspace",
    META_DIR, META_LOGGING_DIR,
)

def is_protected(path: Path) -> bool:
    """判断 path 是否为受保护目录本身或其祖先（删除会波及受保护内容）。"""
    path = path.resolve(strict=False)
    for protected in PROTECTED_DIRS:
        pr = protected.resolve(strict=False)
        if path == pr or path in pr.parents:
            return True
    return False
