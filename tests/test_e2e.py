"""Kohvilogi — E2E testid (End-to-End User Journeys).

Testib terviklikke kasutajateekondi — nagu päris kasutaja kasutaks rakendust.
"""

import pytest
from tests.factories import make_coffee, make_expense_data


class TestE2EFirstUse:
    """E2E: Esmane kasutamine — ava, lisa, vaata."""

    def test_first_use_journey(self, client):
        """Kasutaja avab rakenduse, lisab esimese kohvi, vaatab statistikat."""
        # 1. Ava pealeht
        r = client.get("/")
        assert r.status_code == 200
        assert "Kohvilogi" in r.text

        # 2. Lisa esimene kohv
        r = client.post("/add", data=make_expense_data(
            coffee_type="Espresso", amount="3.50", country="EE"
        ))
        assert r.status_code in (302, 303)

        # 3. Vaata pealehte — kohv nähtaval
        r = client.get("/")
        assert r.status_code == 200

        # 4. Vaata statistikat
        r = client.get("/api/stats")
        d = r.json()
        assert d["total_drinks"] == 1
        assert d["unique_countries"] == 1

        # 5. Vaata maailmakaarti
        r = client.get("/api/world")
        d = r.json()
        assert d["total_countries"] == 1


class TestE2EManageCoffees:
    """E2E: Kohvide haldamine — lisamine, mitu, kustutamine."""

    def test_add_and_delete_journey(self, client):
        """Kasutaja lisab 3 kohvi, kustutab ühe, kontrolli."""
        # Lisa 3 kohvi
        make_coffee(client, coffee_type="Espresso", amount="3.50")
        make_coffee(client, coffee_type="Latte", amount="4.00")
        make_coffee(client, coffee_type="Cappuccino", amount="3.80")

        # Kontrolli, et 3 kohvi
        r = client.get("/api/stats")
        assert r.json()["total_drinks"] == 3

        # Kustuta esimene
        from app.database import get_expenses
        expenses = get_expenses()
        assert len(expenses) == 3
        client.post(f"/delete/{expenses[0]['id']}")

        # Kontrolli, et 2 kohvi
        r = client.get("/api/stats")
        assert r.json()["total_drinks"] == 2


class TestE2EWorldTravel:
    """E2E: Maailma reis — kohvi erinevates riikides."""

    def test_world_travel_journey(self, client):
        """Kasutaja reisib 3 riiki, vaatab top3 ja kaarti."""
        # Lisa kohvi 3 riigis
        make_coffee(client, coffee_type="Espresso", country="EE",
                    latitude="59.44", longitude="24.75")
        make_coffee(client, coffee_type="Latte", country="FI",
                    latitude="60.17", longitude="24.94")
        make_coffee(client, coffee_type="Cappuccino", country="SE",
                    latitude="59.33", longitude="18.07")

        # Vaata maailmakaarti
        r = client.get("/api/world")
        d = r.json()
        assert d["total_countries"] == 3
        assert d["total_drinks"] == 3
        assert len(d["coordinates"]) == 3

        # Vaata top3
        r = client.get("/api/world/top3")
        d = r.json()
        assert "EE" in d
        assert "FI" in d
        assert "SE" in d

        # Vaata riikide kaupa
        r = client.get("/api/world/by-year")
        d = r.json()
        assert len(d) >= 1


class TestE2EStreak:
    """E2E: Streak — järjestikune kohvi joomine."""

    def test_streak_journey(self, client_with_data):
        """Kasutaja näeb streaki ja progressi."""
        # client_with_data juba sisaldab 3 kohvi
        r = client_with_data.get("/api/stats")
        d = r.json()
        assert d["total_drinks"] == 3
        assert d["streak"] >= 1
        assert d["world_progress"] > 0

        # Vaata QR jagamine
        r = client_with_data.get("/api/share")
        d = r.json()
        assert d["total_drinks"] == 3
        assert "share_url" in d


class TestE2EPWA:
    """E2E: PWA — manifest, service worker, offline."""

    def test_pwa_journey(self, client):
        """Kasutaja installib PWA — manifest ja SW olemas."""
        # Manifest
        r = client.get("/manifest.json")
        assert r.status_code == 200
        d = r.json()
        assert d["name"] == "Kohvilogi"
        assert d["display"] == "standalone"
        assert "icons" in d

        # Service Worker
        r = client.get("/sw.js")
        assert r.status_code == 200
        assert "addEventListener" in r.text
        assert "caches" in r.text

        # Health check
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestE2EQRShare:
    """E2E: QR jagamine — jagatud link."""

    def test_share_journey(self, client_with_data):
        """Kasutaja saab jagada oma statistikat."""
        r = client_with_data.get("/api/share")
        assert r.status_code == 200
        d = r.json()
        assert "☕" in d["text"]
        assert "share_url" in d
        assert d["total_drinks"] == 3
        assert d["unique_countries"] == 2
        assert d["streak"] >= 1
