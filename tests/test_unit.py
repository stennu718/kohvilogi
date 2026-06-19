"""Kohvilogi — ühiktestid (Unit Tests).

Testib database.py funktsioone otse, ilma HTTP-taheta.
"""

import os
import tempfile
import pytest
from datetime import date, timedelta


@pytest.fixture
def db():
    """Loo ajutine andmebaas ja taga ühendus."""
    old_db = os.environ.get("DB_PATH")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    os.environ["DB_PATH"] = db_path

    import importlib
    import app.database
    importlib.reload(app.database)
    app.database.init_db()

    yield db_path

    if os.path.exists(db_path):
        os.unlink(db_path)
    if old_db:
        os.environ["DB_PATH"] = old_db
    else:
        os.environ.pop("DB_PATH", None)


class TestInitDb:
    """init_db — lauad ja indeksid."""

    def test_init_creates_expenses_table(self, db):
        from app.database import get_db
        conn = get_db()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'"
        ).fetchall()
        conn.close()
        assert len(tables) == 1

    def test_init_creates_coffee_countries_table(self, db):
        from app.database import get_db
        conn = get_db()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='coffee_countries'"
        ).fetchall()
        conn.close()
        assert len(tables) == 1

    def test_init_idempotent(self, db):
        """init_db võib kutsuda mitu korda — ei tekita vigu."""
        from app.database import init_db
        init_db()  # teine kutse
        # Ei peaks erandi viskama


class TestAddExpense:
    """add_expense — kohvi lisamine."""

    def test_add_basic(self, db):
        from app.database import add_expense
        rowid = add_expense(item="Espresso", amount=3.50)
        assert rowid > 0

    def test_add_with_all_fields(self, db):
        from app.database import add_expense
        rowid = add_expense(
            item="Latte", coffee_type="Latte", amount=4.00,
            currency="EUR", notes="Test", location="Tallinn",
            country="EE", latitude=59.44, longitude=24.75,
        )
        assert rowid > 0

    def test_add_default_date_is_today(self, db):
        from app.database import add_expense, get_db
        add_expense(item="Espresso", amount=3.50)
        conn = get_db()
        row = conn.execute("SELECT date FROM expenses LIMIT 1").fetchone()
        conn.close()
        assert row["date"] == date.today().strftime("%Y-%m-%d")

    def test_add_custom_date(self, db):
        from app.database import add_expense, get_db
        add_expense(item="Espresso", amount=3.50, date="2025-01-15")
        conn = get_db()
        row = conn.execute("SELECT date FROM expenses LIMIT 1").fetchone()
        conn.close()
        assert row["date"] == "2025-01-15"

    def test_add_default_currency_eur(self, db):
        from app.database import add_expense, get_db
        add_expense(item="Espresso", amount=3.50)
        conn = get_db()
        row = conn.execute("SELECT currency FROM expenses LIMIT 1").fetchone()
        conn.close()
        assert row["currency"] == "EUR"

    def test_add_multiple(self, db):
        from app.database import add_expense, get_db
        for i in range(5):
            add_expense(item=f"Coffee {i}", amount=3.0 + i)
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) as cnt FROM expenses").fetchone()["cnt"]
        conn.close()
        assert count == 5


class TestGetExpenses:
    """get_expenses — kohvide lugemine."""

    def test_get_all(self, db):
        from app.database import add_expense, get_expenses
        add_expense(item="Espresso", amount=3.50)
        add_expense(item="Latte", amount=4.00)
        rows = get_expenses()
        assert len(rows) == 2

    def test_get_by_date(self, db):
        from app.database import add_expense, get_expenses
        add_expense(item="Espresso", amount=3.50, date="2025-06-01")
        add_expense(item="Latte", amount=4.00, date="2025-06-02")
        rows = get_expenses(date="2025-06-01")
        assert len(rows) == 1
        assert rows[0]["item"] == "Espresso"

    def test_get_limit(self, db):
        from app.database import add_expense, get_expenses
        for i in range(10):
            add_expense(item=f"Coffee {i}", amount=3.0)
        rows = get_expenses(limit=3)
        assert len(rows) == 3

    def test_get_empty(self, db):
        from app.database import get_expenses
        rows = get_expenses()
        assert rows == []

    def test_get_returns_dicts(self, db):
        from app.database import add_expense, get_expenses
        add_expense(item="Espresso", amount=3.50)
        rows = get_expenses()
        assert isinstance(rows[0], dict)
        assert "id" in rows[0]
        assert "amount" in rows[0]


class TestGetTodayTotal:
    """get_today_total — tänane kogusumma."""

    def test_today_total_empty(self, db):
        from app.database import get_today_total
        totals = get_today_total()
        assert totals == {}

    def test_today_total_with_data(self, db):
        from app.database import add_expense, get_today_total
        add_expense(item="Espresso", amount=3.50, currency="EUR")
        add_expense(item="Latte", amount=4.00, currency="EUR")
        totals = get_today_total()
        assert "EUR" in totals
        assert totals["EUR"] == 7.5

    def test_today_total_multiple_currencies(self, db):
        from app.database import add_expense, get_today_total
        add_expense(item="Espresso", amount=3.50, currency="EUR")
        add_expense(item="Latte", amount=5.00, currency="USD")
        totals = get_today_total()
        assert totals["EUR"] == 3.5
        assert totals["USD"] == 5.0

    def test_today_total_only_today(self, db):
        from app.database import add_expense, get_today_total
        add_expense(item="Yesterday", amount=10.00, date="2020-01-01")
        add_expense(item="Today", amount=3.50)
        totals = get_today_total()
        assert totals["EUR"] == 3.5


class TestGetDailySummary:
    """get_daily_summary — päevakokkuvõte."""

    def test_summary_empty(self, db):
        from app.database import get_daily_summary
        rows = get_daily_summary()
        assert rows == []

    def test_summary_groups_by_date_currency(self, db):
        from app.database import add_expense, get_daily_summary
        add_expense(item="Espresso", amount=3.50, currency="EUR", date="2025-06-01")
        add_expense(item="Latte", amount=4.00, currency="EUR", date="2025-06-01")
        rows = get_daily_summary()
        assert len(rows) >= 1
        # Kontrolli, et tulemus sisaldab count ja total
        assert "count" in rows[0]
        assert "total" in rows[0]


class TestDeleteExpense:
    """delete_expense — kohvi kustutamine."""

    def test_delete_existing(self, db):
        from app.database import add_expense, delete_expense, get_db
        rowid = add_expense(item="Espresso", amount=3.50)
        result = delete_expense(rowid)
        assert result is True
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) as cnt FROM expenses").fetchone()["cnt"]
        conn.close()
        assert count == 0

    def test_delete_nonexistent(self, db):
        from app.database import delete_expense
        result = delete_expense(9999)
        assert result is False

    def test_delete_does_not_affect_others(self, db):
        from app.database import add_expense, delete_expense, get_db
        id1 = add_expense(item="Espresso", amount=3.50)
        add_expense(item="Latte", amount=4.00)
        delete_expense(id1)
        conn = get_db()
        count = conn.execute("SELECT COUNT(*) as cnt FROM expenses").fetchone()["cnt"]
        conn.close()
        assert count == 1


class TestGetMonthlyStats:
    """get_monthly_stats — kuustatistika."""

    def test_monthly_empty(self, db):
        from app.database import get_monthly_stats
        data = get_monthly_stats("2025-01")
        assert data["by_currency"] == {}
        assert data["favorites"] == []
        assert data["daily"] == []

    def test_monthly_with_data(self, db):
        from app.database import add_expense, get_monthly_stats
        add_expense(item="Espresso", amount=3.50, currency="EUR", date="2025-06-01", coffee_type="Espresso")
        add_expense(item="Latte", amount=4.00, currency="EUR", date="2025-06-01", coffee_type="Latte")
        add_expense(item="Espresso", amount=3.50, currency="EUR", date="2025-06-02", coffee_type="Espresso")
        data = get_monthly_stats("2025-06")
        assert "EUR" in data["by_currency"]
        assert data["by_currency"]["EUR"]["count"] == 3
        assert len(data["favorites"]) >= 1
        assert data["favorites"][0]["type"] == "Espresso"
        assert data["favorites"][0]["count"] == 2

    def test_monthly_daily_breakdown(self, db):
        from app.database import add_expense, get_monthly_stats
        add_expense(item="Espresso", amount=3.50, date="2025-06-10", coffee_type="Espresso")
        data = get_monthly_stats("2025-06")
        assert len(data["daily"]) >= 1
        assert data["daily"][0]["count"] >= 1

    def test_monthly_by_type(self, db):
        from app.database import add_expense, get_monthly_stats
        add_expense(item="Espresso", amount=3.50, date="2025-06-01", coffee_type="Espresso")
        add_expense(item="Latte", amount=4.00, date="2025-06-01", coffee_type="Latte")
        data = get_monthly_stats("2025-06")
        types = [t["type"] for t in data["by_type"]]
        assert "Espresso" in types
        assert "Latte" in types


class TestGetWorldStats:
    """get_world_stats — maailma statistika."""

    def test_world_empty(self, db):
        from app.database import get_world_stats
        data = get_world_stats()
        assert data["total_countries"] == 0
        assert data["total_drinks"] == 0
        assert data["countries"] == []

    def test_world_with_data(self, db):
        from app.database import add_expense, get_world_stats
        add_expense(item="Espresso", amount=3.50, country="EE", latitude=59.44, longitude=24.75)
        add_expense(item="Latte", amount=4.00, country="FI", latitude=60.17, longitude=24.94)
        data = get_world_stats()
        assert data["total_countries"] == 2
        assert data["total_drinks"] == 2
        assert len(data["countries"]) == 2

    def test_world_coordinates(self, db):
        from app.database import add_expense, get_world_stats
        add_expense(item="Espresso", amount=3.50, country="EE", latitude=59.44, longitude=24.75)
        data = get_world_stats()
        assert len(data["coordinates"]) == 1
        assert data["coordinates"][0]["latitude"] == 59.44

    def test_world_passport(self, db):
        from app.database import add_expense, get_world_stats
        add_expense(item="Espresso", amount=3.50, country="EE", date="2025-06-01")
        data = get_world_stats()
        assert len(data["passport"]) == 1
        assert data["passport"][0]["country"] == "EE"

    def test_world_excludes_zero_coordinates(self, db):
        from app.database import add_expense, get_world_stats
        add_expense(item="Espresso", amount=3.50, country="EE")  # lat=0, lon=0
        data = get_world_stats()
        assert len(data["coordinates"]) == 0


class TestCoffeeCountries:
    """upsert_coffee_country / get_coffee_countries."""

    def test_upsert_new(self, db):
        from app.database import upsert_coffee_country
        rowid = upsert_coffee_country("EE", "Eesti", "🇪🇪")
        assert rowid > 0

    def test_upsert_update(self, db):
        from app.database import upsert_coffee_country
        upsert_coffee_country("EE", "Eesti", "🇪🇪")
        rowid = upsert_coffee_country("EE", "Eesti Uuendatud", "🇪🇪")
        assert rowid > 0

    def test_get_countries_empty(self, db):
        from app.database import get_coffee_countries
        rows = get_coffee_countries()
        assert rows == []

    def test_get_countries_with_data(self, db):
        from app.database import upsert_coffee_country, get_coffee_countries
        upsert_coffee_country("EE", "Eesti", "🇪🇪")
        upsert_coffee_country("FI", "Soome", "🇫🇮")
        rows = get_coffee_countries()
        assert len(rows) == 2
        # Kontrolli, et tagastab dict'idena
        assert isinstance(rows[0], dict)
        assert "country_code" in rows[0]
