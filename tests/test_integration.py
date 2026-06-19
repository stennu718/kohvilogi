"""Kohvilogi — integratsioonitestid (Integration Tests).

Testib API endpointe koos andmebaasiga — terviklik süsteemi käitumine.
"""

import pytest
from tests.factories import make_coffee, make_expense_data


class TestAddEndpoint:
    """POST /add — kohvi lisamine."""

    def test_add_redirects(self, client):
        r = client.post("/add", data=make_expense_data())
        assert r.status_code in (302, 303)

    def test_add_creates_record(self, client):
        client.post("/add", data=make_expense_data(coffee_type="Espresso"))
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) == 1
        assert expenses[0]["coffee_type"] == "Espresso"

    def test_add_default_currency(self, client):
        client.post("/add", data=make_expense_data(coffee_type="Latte", amount="4.00"))
        from app.database import get_expenses
        expenses = get_expenses()
        assert expenses[0]["currency"] == "EUR"

    def test_add_comma_decimal(self, client):
        r = client.post("/add", data=make_expense_data(amount="3,50"))
        assert r.status_code in (302, 303)

    def test_add_invalid_amount_silently_redirects(self, client):
        """Vigane amount (mitu number) — ei erita, lihtsalt redirect."""
        r = client.post("/add", data=make_expense_data(amount="abc"))
        assert r.status_code in (302, 303)

    def test_add_with_country_and_coords(self, client):
        client.post("/add", data=make_expense_data(
            country="EE", latitude="59.44", longitude="24.75"
        ))
        from app.database import get_expenses
        expenses = get_expenses()
        assert expenses[0]["country"] == "EE"
        assert expenses[0]["latitude"] == 59.44

    def test_add_multiple_coffees(self, client):
        for i in range(3):
            client.post("/add", data=make_expense_data(coffee_type=f"Coffee {i}"))
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) == 3


class TestDeleteEndpoint:
    """POST /delete/{id} — kohvi kustutamine."""

    def test_delete_redirects(self, client):
        make_coffee(client)
        from app.database import get_expenses
        expenses = get_expenses()
        r = client.post(f"/delete/{expenses[0]['id']}")
        assert r.status_code in (302, 303)

    def test_delete_removes_record(self, client):
        make_coffee(client)
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) == 1
        client.post(f"/delete/{expenses[0]['id']}")
        expenses = get_expenses()
        assert len(expenses) == 0

    def test_delete_nonexistent(self, client):
        """Olematu id — peaks redirectima (ei erita)."""
        r = client.post("/delete/9999")
        assert r.status_code in (302, 303)


class TestApiStats:
    """GET /api/stats — statistika API."""

    def test_stats_empty(self, client):
        r = client.get("/api/stats")
        assert r.status_code == 200
        d = r.json()
        assert d["total_drinks"] == 0
        assert d["unique_countries"] == 0
        assert d["streak"] == 0

    def test_stats_with_data(self, client):
        make_coffee(client, country="EE")
        make_coffee(client, country="FI")
        r = client.get("/api/stats")
        d = r.json()
        assert d["total_drinks"] == 2
        assert d["unique_countries"] == 2

    def test_stats_streak(self, client):
        """Streak vähemalt 1 kui täna on kohv."""
        make_coffee(client)
        r = client.get("/api/stats")
        d = r.json()
        assert d["streak"] >= 1

    def test_stats_response_structure(self, client):
        r = client.get("/api/stats")
        d = r.json()
        assert "streak" in d
        assert "total_drinks" in d
        assert "unique_countries" in d
        assert "world_progress" in d
        assert "week_drinks" in d


class TestApiWorld:
    """GET /api/world — maailma kaart API."""

    def test_world_empty(self, client):
        r = client.get("/api/world")
        assert r.status_code == 200
        d = r.json()
        assert d["total_countries"] == 0
        assert d["total_drinks"] == 0
        assert "regions" in d
        assert len(d["regions"]) == 28

    def test_world_with_data(self, client):
        make_coffee(client, country="EE", latitude="59.44", longitude="24.75")
        r = client.get("/api/world")
        d = r.json()
        assert d["total_countries"] == 1
        assert d["total_drinks"] == 1
        assert len(d["coordinates"]) == 1

    def test_world_enriched_country_data(self, client):
        make_coffee(client, country="EE")
        r = client.get("/api/world")
        d = r.json()
        countries = d["countries"]
        assert len(countries) == 1
        assert "flag" in countries[0]
        assert "country_name" in countries[0]


class TestApiWorldTop3:
    """GET /api/world/top3 — top 3 kohvi riigi kohta."""

    def test_top3_empty(self, client):
        r = client.get("/api/world/top3")
        assert r.status_code == 200
        assert r.json() == {}

    def test_top3_with_data(self, client):
        make_coffee(client, coffee_type="Espresso", country="EE")
        make_coffee(client, coffee_type="Espresso", country="EE")
        make_coffee(client, coffee_type="Latte", country="EE")
        make_coffee(client, coffee_type="Cappuccino", country="FI")
        r = client.get("/api/world/top3")
        d = r.json()
        assert "EE" in d
        assert "FI" in d
        assert len(d["EE"]["coffees"]) == 2
        assert d["EE"]["coffees"][0]["type"] == "Espresso"
        assert d["EE"]["coffees"][0]["count"] == 2

    def test_top3_max_three_per_country(self, client):
        """Rohkem kui 3 kohvi tüüpi — ainult top 3."""
        for coffee in ["Espresso", "Latte", "Cappuccino", "Mocha", "Americano"]:
            make_coffee(client, coffee_type=coffee, country="EE")
        r = client.get("/api/world/top3")
        d = r.json()
        assert len(d["EE"]["coffees"]) == 3


class TestApiWorldByYear:
    """GET /api/world/by-year — aastade kaupa."""

    def test_by_year_empty(self, client):
        r = client.get("/api/world/by-year")
        assert r.status_code == 200
        assert r.json() == {}

    def test_by_year_with_data(self, client):
        make_coffee(client, country="EE")
        r = client.get("/api/world/by-year")
        d = r.json()
        import datetime
        year = str(datetime.date.today().year)
        assert year in d
        assert d[year]["total"] >= 1


class TestApiShare:
    """GET /api/share — jagamine."""

    def test_share_structure(self, client):
        r = client.get("/api/share")
        assert r.status_code == 200
        d = r.json()
        assert "text" in d
        assert "share_url" in d
        assert "total_drinks" in d
        assert "☕" in d["text"]

    def test_share_with_data(self, client):
        make_coffee(client, country="EE")
        r = client.get("/api/share")
        d = r.json()
        assert d["total_drinks"] == 1


class TestStatsPage:
    """GET /stats — statistika leht."""

    def test_stats_page_default(self, client):
        r = client.get("/stats")
        assert r.status_code == 200

    def test_stats_page_with_month(self, client):
        r = client.get("/stats?month=2025-06")
        assert r.status_code == 200

    def test_stats_page_with_data(self, client):
        make_coffee(client, coffee_type="Espresso")
        r = client.get("/stats")
        assert r.status_code == 200


class TestHealthEndpoint:
    """GET /health — tervisekontroll."""

    def test_health_ok(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
        assert d["app"] == "kohvilogi"
        assert "version" in d


class TestPWAManifest:
    """GET /manifest.json — PWA manifest."""

    def test_manifest_ok(self, client):
        r = client.get("/manifest.json")
        assert r.status_code == 200
        d = r.json()
        assert d["name"] == "Kohvilogi"
        assert d["display"] == "standalone"

    def test_manifest_has_icons(self, client):
        r = client.get("/manifest.json")
        d = r.json()
        assert "icons" in d
        assert len(d["icons"]) > 0


class TestServiceWorker:
    """GET /sw.js — Service Worker."""

    def test_sw_returns_js(self, client):
        r = client.get("/sw.js")
        assert r.status_code == 200
        assert "addEventListener" in r.text

    def test_sw_has_cache_logic(self, client):
        r = client.get("/sw.js")
        assert "caches" in r.text
