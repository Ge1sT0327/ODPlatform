"""odp-reset: 清理运行时产物，回退到 clone 初态。"""

import sys
import shutil
import argparse
from pathlib import Path
from odp_platform.common.paths import get_dirs_to_reset, is_protected
from odp_platform.common.constants import ExitCode

def main(argv: list = None) -> int:
    parser = argparse.ArgumentParser(description="重置项目到 clone 初态")
    parser.add_argument("--dry-run", action="store_true", help="仅列出将删除的目录")
    parser.add_argument("--yes", action="store_true", help="跳过确认提示")
    args = parser.parse_args(argv)

    dirs = get_dirs_to_reset()
    # 过滤掉受保护的
    safe = [d for d in dirs if d.exists() and not is_protected(d)]

    if args.dry_run:
        print("将删除以下目录:")
        for d in safe:
            print(f"  - {d}")
        return ExitCode.SUCCESS

    if not args.yes:
        resp = input(f"确认删除 {len(safe)} 个运行时目录? [y/N]: ")
        if resp.lower() != "y":
            print("已取消。")
            return ExitCode.SUCCESS

    for d in safe:
        if d.exists():
            shutil.rmtree(d)
    print(f"odp-reset: 已清理 {len(safe)} 个目录。")
    return ExitCode.SUCCESS

if __name__ == "__main__":
    sys.exit(main())
