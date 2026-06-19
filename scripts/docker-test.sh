#!/usr/bin/env bash
# Kohvilogi — Docker testimise proov
# Ehitab Docker image'i, käivitab testid containeris, näitab tulemust

set -euo pipefail

cd "$(dirname "$0")/.."

IMAGE="kohvilogi:test"

echo "=== Kohvilogi Docker Test Proov ==="
echo ""

# 1. Ehita image
echo "[1/4] Ehitan Docker image'i..."
docker build -t "$IMAGE" .

# 2. Käivita testid containeris
echo ""
echo "[2/4] Käivitan teste containeris..."
docker run --rm "$IMAGE" sh -c "
    pip install -q -e '.[test]' 2>/dev/null
    pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=80 -v --tb=short
"

# 3. Käivita rakendus taga ja testi läbi
echo ""
echo "[3/4] Käivitan rakendust taustal..."
docker run -d --name kohvilogi-test -p 8000:8000 "$IMAGE" 2>/dev/null

# Oota kuni rakendus tööle hakkab
echo "    Ootan kuni rakendus on valmis..."
for i in $(seq 1 15); do
    if curl -s http://localhost:8000/health | grep -q "ok" 2>/dev/null; then
        echo "    ✅ Rakendus töötab pordil 8000"
        break
    fi
    sleep 1
done

# 4. Testi endpointe
echo ""
echo "[4/4] Testin endpointe..."

echo -n "    GET /health → "
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "FAIL"

echo -n "    GET / → "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$STATUS" = "200" ]; then
    echo "✅ 200 OK"
else
    echo "❌ $STATUS"
fi

echo -n "    GET /api/stats → "
curl -s http://localhost:8000/api/stats | python3 -m json.tool 2>/dev/null || echo "FAIL"

echo -n "    GET /api/world → "
curl -s http://localhost:8000/api/world | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ {d[\"total_countries\"]} riiki, {len(d[\"regions\"])} piirkonda')" 2>/dev/null || echo "FAIL"

echo -n "    GET /manifest.json → "
curl -s http://localhost:8000/manifest.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ {d[\"name\"]} — {d[\"display\"]}')" 2>/dev/null || echo "FAIL"

echo -n "    POST /add → "
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost:8000/add -d "coffee_type=Espresso&amount=3.50&country=EE")
if [ "$STATUS" = "303" ] || [ "$STATUS" = "302" ]; then
    echo "✅ $STATUS redirect"
else
    echo "❌ $STATUS"
fi

echo -n "    GET /api/stats (pärast lisamist) → "
curl -s http://localhost:8000/api/stats | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'✅ {d[\"total_drinks\"]} kohvi, {d[\"unique_countries\"]} riik, streak={d[\"streak\"]}')" 2>/dev/null || echo "FAIL"

# Puhasta
echo ""
echo "Puhastan test container'i..."
docker stop kohvilogi-test 2>/dev/null
docker rm kohvilogi-test 2>/dev/null
docker rmi "$IMAGE" 2>/dev/null

echo ""
echo "=== Docker test proov lõpetatud ==="
