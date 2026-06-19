"""Kohvilogi — turvalisus- ja jõudlustestid (Security + Performance).

Testib SQL injection'i, XSS-i, piiranguid ja koormust.
"""

import pytest
from tests.factories import make_coffee, make_expense_data


class TestSQLInjection:
    """SQL injection vastupidavus."""

    def test_sql_injection_in_country(self, client):
        """SQL injection country väljas — ei tohi murda andmebaasi."""
        r = client.post("/add", data=make_expense_data(
            country="EE'; DROP TABLE expenses; --"
        ))
        # Peaks redirectima (ignoreerib), mitte erutama
        assert r.status_code in (302, 303)
        # Kontrolli, et tabel on ikka olemas
        r = client.get("/api/stats")
        assert r.status_code == 200

    def test_sql_injection_in_notes(self, client):
        """SQL injection notes väljas."""
        r = client.post("/add", data=make_expense_data(
            notes="'; DELETE FROM expenses; --"
        ))
        assert r.status_code in (302, 303)
        # Andmebaas peab töötama
        r = client.get("/health")
        assert r.status_code == 200

    def test_sql_injection_in_location(self, client):
        """SQL injection location väljas."""
        r = client.post("/add", data=make_expense_data(
            location="Tallinn'; DROP TABLE expenses; --"
        ))
        assert r.status_code in (302, 303)
        r = client.get("/api/stats")
        assert r.status_code == 200

    def test_sql_injection_in_delete(self, client):
        """SQL injection delete URL-is — ei tohi erutada.
        FastAPI valideerib int path param'i, seega 422 on oodatud."""
        make_coffee(client)
        r = client.post("/delete/1 OR 1=1")
        # FastAPI ei luba mitte-int path param — 422 on korrektne
        assert r.status_code == 422


class TestXSS:
    """XSS vastupidavus."""

    def test_xss_in_notes(self, client):
        """XSS notes väljas — ei tohi täita skripti."""
        r = client.post("/add", data=make_expense_data(
            notes="<script>alert('xss')</script>"
        ))
        assert r.status_code in (302, 303)
        # Kontrolli, et pealeht töötab
        r = client.get("/")
        assert r.status_code == 200

    def test_xss_in_location(self, client):
        """XSS location väljas."""
        r = client.post("/add", data=make_expense_data(
            location="<img src=x onerror=alert(1)>"
        ))
        assert r.status_code in (302, 303)
        r = client.get("/")
        assert r.status_code == 200

    def test_xss_in_coffee_type(self, client):
        """XSS coffee_type väljas."""
        r = client.post("/add", data=make_expense_data(
            coffee_type="<script>alert('xss')</script>"
        ))
        assert r.status_code in (302, 303)


class TestInputValidation:
    """Sisendi valideerimise piirangud."""

    def test_negative_amount(self, client):
        """Negatiivne summa — peaks redirectima."""
        r = client.post("/add", data=make_expense_data(amount="-100"))
        assert r.status_code in (302, 303)

    def test_zero_amount(self, client):
        """Null summa — peaks redirectima."""
        r = client.post("/add", data=make_expense_data(amount="0"))
        assert r.status_code in (302, 303)

    def test_very_large_amount(self, client):
        """Väga suur summa."""
        r = client.post("/add", data=make_expense_data(amount="999999.99"))
        assert r.status_code in (302, 303)

    def test_empty_coffee_type(self, client):
        """Tühi coffee_type — FastAPI Form(...) nõuab, seega 422."""
        r = client.post("/add", data=make_expense_data(coffee_type=""))
        # Form(...) required — tühi string ei läbi valideerimist
        assert r.status_code == 422

    def test_long_notes(self, client):
        """Väga pikk notes — ei tohi erutada."""
        r = client.post("/add", data=make_expense_data(
            notes="A" * 5000
        ))
        assert r.status_code in (302, 303)

    def test_long_location(self, client):
        """Väga pikk location — ei tohi erutada."""
        r = client.post("/add", data=make_expense_data(
            location="B" * 5000
        ))
        assert r.status_code in (302, 303)

    def test_special_chars_in_country(self, client):
        """Erimärgid country väljas."""
        r = client.post("/add", data=make_expense_data(
            country="<script>alert(1)</script>"
        ))
        assert r.status_code in (302, 303)

    def test_unicode_in_notes(self, client):
        """Unicode notes väljas."""
        r = client.post("/add", data=make_expense_data(
            notes="☕🍵 Кофе 咖啡 قهوة"
        ))
        assert r.status_code in (302, 303)


class TestPerformance:
    """Jõudlustestid."""

    def test_add_100_coffees(self, client):
        """100 kohvi lisamine — ei tohi olla liiga aeglane."""
        import time
        start = time.time()
        for i in range(100):
            client.post("/add", data=make_expense_data(
                coffee_type="Espresso",
                amount=str(3.0 + (i % 10) * 0.1),
            ))
        elapsed = time.time() - start
        # 100 kohvi peaks võtma alla 5 sekundit
        assert elapsed < 5.0, f"100 coffees took {elapsed:.2f}s"

    def test_stats_with_100_records(self, client):
        """Statistika päring 100 kohviga — kiire."""
        import time
        for i in range(100):
            client.post("/add", data=make_expense_data(
                country="EE" if i % 2 == 0 else "FI",
                latitude=str(59.0 + i * 0.01),
                longitude=str(24.0 + i * 0.01),
            ))
        start = time.time()
        r = client.get("/api/stats")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 1.0, f"Stats query took {elapsed:.2f}s"

    def test_world_with_100_records(self, client):
        """Maailma päring 100 kohviga — kiire."""
        for i in range(100):
            client.post("/add", data=make_expense_data(
                country="EE" if i % 2 == 0 else "FI",
                latitude=str(59.0 + i * 0.01),
                longitude=str(24.0 + i * 0.01),
            ))
        import time
        start = time.time()
        r = client.get("/api/world")
        elapsed = time.time() - start
        assert r.status_code == 200
        assert elapsed < 1.0, f"World query took {elapsed:.2f}s"
