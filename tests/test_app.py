import os
import tempfile
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a fresh test client with a clean temp database for EACH test."""
    # Remove old DB_PATH so init_db() creates a fresh one
    old_db = os.environ.get("DB_PATH")
    old_env = os.environ.get("ENV")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    os.environ["DB_PATH"] = db_path
    os.environ["ENV"] = "testing"

    # Re-import to pick up new DB_PATH
    import importlib
    import app.database
    import app.config
    importlib.reload(app.database)
    importlib.reload(app.config)
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
    if old_env:
        os.environ["ENV"] = old_env
    else:
        os.environ.pop("ENV", None)


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


class TestNewEndpoints:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
        assert d["app"] == "kohvilogi"
        assert "version" in d

    def test_api_stats(self, client):
        r = client.get("/api/stats")
        assert r.status_code == 200
        d = r.json()
        assert "streak" in d
        assert "total_drinks" in d
        assert "unique_countries" in d
        assert "world_progress" in d
        assert "week_drinks" in d

    def test_api_world_top3_empty(self, client):
        r = client.get("/api/world/top3")
        assert r.status_code == 200
        assert r.json() == {}

    def test_api_world_top3_with_data(self, client):
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50", "country": "EE"})
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50", "country": "EE"})
        client.post("/add", data={"coffee_type": "Latte", "amount": "4.00", "country": "EE"})
        client.post("/add", data={"coffee_type": "Cappuccino", "amount": "4.00", "country": "FI"})
        r = client.get("/api/world/top3")
        d = r.json()
        assert "EE" in d
        assert "FI" in d
        assert len(d["EE"]["coffees"]) == 2  # Espresso and Latte
        assert d["EE"]["coffees"][0]["type"] == "Espresso"  # Most common first
        assert d["EE"]["coffees"][0]["count"] == 2

    def test_api_world_by_year_empty(self, client):
        r = client.get("/api/world/by-year")
        assert r.status_code == 200
        assert r.json() == {}

    def test_api_world_by_year_with_data(self, client):
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50", "country": "EE"})
        r = client.get("/api/world/by-year")
        d = r.json()
        import datetime
        year = str(datetime.date.today().year)
        assert year in d
        assert d[year]["total"] >= 1

    def test_api_share(self, client):
        r = client.get("/api/share")
        assert r.status_code == 200
        d = r.json()
        assert "text" in d
        assert "share_url" in d
        assert "total_drinks" in d
        assert "☕" in d["text"]


class TestAPIV1:
    """Tests for the new v1 API namespace."""

    def test_v1_info(self, client):
        """API v1 root returns endpoint listing."""
        r = client.get("/api/v1")
        assert r.status_code == 200
        d = r.json()
        assert "version" in d
        assert "endpoints" in d
        assert "auth" in d

    def test_v1_expenses_list(self, client):
        """GET /api/v1/expenses lists expenses."""
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50"})
        r = client.get("/api/v1/expenses")
        assert r.status_code == 200
        d = r.json()
        assert d["success"] is True
        assert d["count"] == 1

    def test_v1_expenses_create_json(self, client):
        """POST /api/v1/expenses with JSON body creates a record."""
        r = client.post("/api/v1/expenses", json={
            "coffee_type": "Espresso",
            "amount": 3.50,
            "currency": "EUR",
            "notes": "API test",
            "country": "EE",
        })
        assert r.status_code == 201
        d = r.json()
        assert d["success"] is True
        assert d["id"] > 0

    def test_v1_expenses_create_invalid_type(self, client):
        """POST /api/v1/expenses with invalid coffee type returns 400."""
        r = client.post("/api/v1/expenses", json={
            "coffee_type": "invalid-coffee",
            "amount": 3.50,
        })
        assert r.status_code == 400

    def test_v1_expenses_create_negative_amount(self, client):
        """POST /api/v1/expenses with negative amount returns 400."""
        r = client.post("/api/v1/expenses", json={
            "coffee_type": "Espresso",
            "amount": -5,
        })
        assert r.status_code == 400

    def test_v1_stats(self, client):
        """GET /api/v1/stats returns dashboard statistics."""
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50", "country": "EE"})
        r = client.get("/api/v1/stats")
        assert r.status_code == 200
        d = r.json()
        assert d["total_drinks"] == 1
        assert d["unique_countries"] == 1

    def test_v1_world(self, client):
        """GET /api/v1/world returns world data."""
        r = client.get("/api/v1/world")
        assert r.status_code == 200
        d = r.json()
        assert "regions" in d
        assert "countries" in d

    def test_v1_expenses_delete(self, client):
        """POST /api/v1/expenses/{id} deletes an expense."""
        client.post("/add", data={"coffee_type": "Espresso", "amount": "3.50"})
        from app.database import get_expenses
        expenses = get_expenses()
        expense_id = expenses[0]["id"]
        r = client.post(f"/api/v1/expenses/{expense_id}")
        assert r.status_code == 200
        d = r.json()
        assert d["success"] is True

    def test_v1_expenses_delete_nonexistent(self, client):
        """POST /api/v1/expenses/9999 returns 404."""
        r = client.post("/api/v1/expenses/9999")
        assert r.status_code == 404


class TestAuthEndpoints:
    """Tests for authentication endpoints."""

    def test_register(self, client):
        """POST /api/v1/auth/register creates a user."""
        r = client.post("/api/v1/auth/register", data={
            "username": "testuser",
            "password": "testpass123",
        })
        assert r.status_code == 200
        d = r.json()
        assert d["success"] is True
        assert "token" in d

    def test_register_duplicate(self, client):
        """Registering same username twice returns 409."""
        client.post("/api/v1/auth/register", data={
            "username": "testuser",
            "password": "testpass123",
        })
        r = client.post("/api/v1/auth/register", data={
            "username": "testuser",
            "password": "testpass123",
        })
        assert r.status_code == 409

    def test_login(self, client):
        """POST /api/v1/auth/login returns a token."""
        client.post("/api/v1/auth/register", data={
            "username": "testuser",
            "password": "testpass123",
        })
        r = client.post("/api/v1/auth/login", data={
            "username": "testuser",
            "password": "testpass123",
        })
        assert r.status_code == 200
        d = r.json()
        assert d["success"] is True
        assert "token" in d

    def test_login_wrong_password(self, client):
        """Login with wrong password returns 401."""
        client.post("/api/v1/auth/register", data={
            "username": "testuser",
            "password": "testpass123",
        })
        r = client.post("/api/v1/auth/login", data={
            "username": "testuser",
            "password": "wrongpass",
        })
        assert r.status_code == 401

    def test_register_short_password(self, client):
        """Register with too-short password returns 400."""
        r = client.post("/api/v1/auth/register", data={
            "username": "testuser",
            "password": "short",
        })
        assert r.status_code == 400
