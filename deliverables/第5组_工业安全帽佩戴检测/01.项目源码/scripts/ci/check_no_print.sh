#!/bin/bash
# 检查业务模块是否有裸 print（排除 CLI 入口和测试）
export LC_ALL=C.utf8
errors=0
for f in $(find apps/platform/src/odp_platform -name "*.py" \
    ! -path "*/cli/*" ! -path "*/runtime_config/generator.py" \
    ! -path "*/tests/*" ! -name "__init__.py"); do
    if grep -nP '(?<!def )(?<!\.)print\s*\(' "$f"; then
        echo "ERROR: $f contains bare print()"
        errors=$((errors+1))
    fi
done
exit $errors
