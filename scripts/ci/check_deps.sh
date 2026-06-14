#!/bin/bash
export LC_ALL=C.utf8
errors=0

# 优先使用项目虚拟环境 Python
if [ -x ".venv/Scripts/python" ]; then
    PYTHON=".venv/Scripts/python"
elif [ -x ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
else
    PYTHON="python"
fi

# 使用 Python AST 检查真实的 import 语句，避免误伤注释/字符串
_check_import() {
    local dir=$1
    local forbidden=$2
    "$PYTHON" - "$dir" "$forbidden" <<'PY'
import ast, sys
from pathlib import Path
root = Path(sys.argv[1])
forbidden = sys.argv[2]
errors = 0
for f in root.rglob("*.py"):
    if f.name == "__init__.py":
        continue
    try:
        tree = ast.parse(f.read_text(encoding="utf-8"), filename=str(f))
    except Exception:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if forbidden in alias.name.split("."):
                    print(f"{f}:{node.lineno}: import {alias.name}")
                    errors += 1
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if forbidden in module.split("."):
                print(f"{f}:{node.lineno}: from {module} import ...")
                errors += 1
sys.exit(errors)
PY
    return $?
}

# 推理包不得 import training
if ! _check_import apps/platform/src/odp_platform/inference training; then
    echo "ERROR: inference/ imports training/"
    errors=$((errors+1))
fi
# evaluation 不得 import training
if ! _check_import apps/platform/src/odp_platform/evaluation training; then
    echo "ERROR: evaluation/ imports training/"
    errors=$((errors+1))
fi
# frame_source 不得 import odp_platform.common
if ! _check_import apps/platform/src/odp_platform/frame_source odp_platform.common; then
    echo "ERROR: frame_source/ imports odp_platform.common"
    errors=$((errors+1))
fi
exit $errors
