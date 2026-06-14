"""测试路径解析、marker file、get_dirs_to_initialize。"""
import pytest
from pathlib import Path
from odp_platform.common.paths import (
    _find_workspace_root, ROOT_DIR, APP_DIR,
    get_dirs_to_initialize, get_dirs_to_reset, is_protected,
)

def test_workspace_root_exists():
    assert ROOT_DIR.exists()
    assert (ROOT_DIR / ".odp-workspace").exists()

def test_find_workspace_root_raises_in_tmp(tmp_path):
    with pytest.raises(FileNotFoundError):
        _find_workspace_root(tmp_path)

def test_app_dir_is_relative_to_root():
    assert APP_DIR.is_relative_to(ROOT_DIR)

def test_get_dirs_to_initialize_all_relative():
    for d in get_dirs_to_initialize():
        assert isinstance(d, Path)
        # 所有目录都在 ROOT_DIR 下
        assert d.is_relative_to(ROOT_DIR) or d == ROOT_DIR

def test_is_protected_root():
    assert is_protected(ROOT_DIR) is True

def test_get_dirs_to_reset_not_protected():
    for d in get_dirs_to_reset():
        assert is_protected(d) is False
