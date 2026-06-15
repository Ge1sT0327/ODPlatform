"""odp-init: 按需创建运行时目录，幂等操作。"""

import sys
from pathlib import Path
from odp_platform.common.paths import get_dirs_to_initialize, ROOT_DIR
from odp_platform.common.constants import ExitCode

def main(argv: list = None) -> int:
    """
    遍历 get_dirs_to_initialize()，对每个目录执行 mkdir(parents=True, exist_ok=True)。
    对需要纳入版本控制的空目录，写入 .gitkeep 文件。
    返回 ExitCode.SUCCESS。
    """
    try:
        dirs = get_dirs_to_initialize()
        gitkeep_dirs = [
            d for d in dirs
            if not any((d / f).exists() for f in [".gitkeep"])
            and d.is_relative_to(ROOT_DIR)
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        for d in gitkeep_dirs:
            gk = d / ".gitkeep"
            if not gk.exists() and not any(d.iterdir()):
                gk.touch()

        print(f"odp-init: 已确保 {len(dirs)} 个目录就绪。")
        return ExitCode.SUCCESS
    except Exception as e:
        print(f"odp-init 失败: {e}", file=sys.stderr)
        return ExitCode.SYSTEM_ERROR

if __name__ == "__main__":
    sys.exit(main())
