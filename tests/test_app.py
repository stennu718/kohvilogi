import os
import tempfile
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a fresh test client with a clean temp database for EACH test."""
    # Remove old DB_PATH so init_db() creates a fresh one
    old_db = os.environ.get("DB_PATH")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    os.environ["DB_PATH"] = db_path

    # Re-import to pick up new DB_PATH
    import importlib
    import app.database
    importlib.reload(app.database)
    app.database.init_db()

    from app.main import app
    c = TestClient(app, follow_redirects=False)
    yield c

    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)
    if old_db:
        os.environ["DB_PATH"] = old_db
    else:
        os.environ.pop("DB_PATH", None)


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
        assert d["app"] == "kohvilogi"


class TestIndex:
    def test_index_loads(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "Kohvilogi" in r.text

    def test_index_has_form(self, client):
        r = client.get("/")
        assert 'action="/add"' in r.text


class TestAddCoffee:
    def test_add_redirects(self, client):
        r = client.post("/add", data={
            "coffee_type": "Espresso", "amount": "3.50", "currency": "EUR",
            "notes": "Test", "location": "Tallinn", "country": "EE",
            "latitude": "59.44", "longitude": "24.75",
        })
        assert r.status_code in (302, 303)

    def test_add_defaults(self, client):
        r = client.post("/add", data={"coffee_type": "Latte", "amount": "4.00"})
        assert r.status_code in (302, 303)

    def test_add_comma_amount(self, client):
        r = client.post("/add", data={"coffee_type": "Cappuccino", "amount": "3,50"})
        assert r.status_code in (302, 303)

    def test_add_creates_record(self, client):
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50"})
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) == 1
        assert expenses[0]["coffee_type"] == "Espresso"


class TestDelete:
    def test_delete_redirects(self, client):
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50"})
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) > 0
        r = client.post(f"/delete/{expenses[0]['id']}")
        assert r.status_code in (302, 303)

    def test_delete_removes_record(self, client):
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50"})
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) == 1
        client.post(f"/delete/{expenses[0]['id']}")
        expenses = get_expenses()
        assert len(expenses) == 0


class TestStats:
    def test_stats_page(self, client):
        r = client.get("/stats")
        assert r.status_code == 200

    def test_stats_with_month(self, client):
        r = client.get("/stats?month=2025-06")
        assert r.status_code == 200

    def test_api_stats_empty(self, client):
        r = client.get("/api/stats")
        assert r.status_code == 200
        d = r.json()
        assert d["total_drinks"] == 0
        assert d["unique_countries"] == 0
        assert d["streak"] == 0

    def test_api_stats_with_data(self, client):
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50", "country": "EE"})
        client.post("/add", data={"coffee_type": "Latte", "amount": "4.00", "country": "FI"})
        r = client.get("/api/stats")
        d = r.json()
        assert d["total_drinks"] == 2
        assert d["unique_countries"] == 2


class TestWorld:
    def test_map_page(self, client):
        r = client.get("/map")
        assert r.status_code == 200

    def test_api_world_empty(self, client):
        r = client.get("/api/world")
        assert r.status_code == 200
        d = r.json()
        assert d["total_countries"] == 0
        assert d["total_drinks"] == 0
        assert "regions" in d
        assert len(d["regions"]) == 28

    def test_api_world_with_data(self, client):
        client.post("/add", data={
            "coffee_type": "Espresso", "amount": "3.50",
            "country": "EE", "latitude": "59.44", "longitude": "24.75"
        })
        r = client.get("/api/world")
        d = r.json()
        assert d["total_countries"] == 1
        assert d["total_drinks"] == 1
        assert len(d["coordinates"]) == 1


class TestPWA:
    def test_manifest(self, client):
        r = client.get("/manifest.json")
        assert r.status_code == 200
        d = r.json()
        assert d["name"] == "Kohvilogi"
        assert d["display"] == "standalone"

    def test_sw_js(self, client):
        r = client.get("/sw.js")
        assert r.status_code == 200
        assert "addEventListener" in r.text
