#!/usr/bin/env bash
# Kohvilogi — CI test runner (kohalik)
# Kasutamine: ./scripts/ci-test.sh

set -euo pipefail

cd "$(dirname "$0")/.."

echo "=== Kohvilogi CI ==="
echo ""

# 1. Installi deps kui vaja
if [ ! -d ".venv" ]; then
    echo "[1/3] Loov virtuaalkeskkond..."
    python3 -m venv .venv
    .venv/bin/pip install -q -e ".[test]"
else
    echo "[1/3] Virtuaalkeskkond olemas, uuendan..."
    .venv/bin/pip install -q -e ".[test]" 2>/dev/null || true
fi

# 2. Käivita testid koos coverage'iga
echo ""
echo "[2/3] Käivitan teste..."
.venv/bin/pytest tests/ \
    --cov=app \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v --tb=short

# 3. Kokkuvõte
echo ""
echo "[3/3] ✅ Kõik testid läbitud!"
echo ""
echo "Coverage raport: htmlcov/index.html"
echo "Ava brauseris: file://$(pwd)/htmlcov/index.html"
