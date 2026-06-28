import sqlite3
import os
from pathlib import Path
from datetime import datetime

if "DB_PATH" not in os.environ:
    os.environ["DB_PATH"] = "/data/kohvilogi.db"
DB_PATH = Path(os.environ["DB_PATH"])
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            coffee_type TEXT DEFAULT '',
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            date TEXT NOT NULL,
            notes TEXT DEFAULT '',
            location TEXT DEFAULT '',
            country TEXT DEFAULT '',
            latitude REAL DEFAULT 0,
            longitude REAL DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS coffee_countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT NOT NULL UNIQUE,
            country_name TEXT NOT NULL,
            coffee_type TEXT DEFAULT '',
            first_drink_date TEXT DEFAULT '',
            drink_count INTEGER DEFAULT 0,
            flag_emoji TEXT DEFAULT '',
            notes TEXT DEFAULT ''
        )
    """)
    # Performance indexes for common queries
    conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_country ON expenses(country)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_coffee_type ON expenses(coffee_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date_country ON expenses(date, country)")
    conn.commit()
    conn.close()


def add_expense(item: str, amount: float, currency: str = "EUR", coffee_type: str = "",
                date: str | None = None, notes: str = "",
                location: str = "", country: str = "",
                latitude: float = 0, longitude: float = 0) -> int:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO expenses
           (item, coffee_type, amount, currency, date, notes, location, country, latitude, longitude, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (item, coffee_type, amount, currency, date, notes, location, country, latitude, longitude, datetime.now().isoformat()),
    )
    conn.commit()
    rowid = cur.lastrowid or 0
    conn.close()
    return rowid


def get_expenses(date: str | None = None, limit: int = 100) -> list:
    conn = get_db()
    if date:
        rows = conn.execute(
            "SELECT * FROM expenses WHERE date = ? ORDER BY created_at DESC LIMIT ?",
            (date, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM expenses ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_today_total() -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    rows = conn.execute(
        "SELECT currency, COALESCE(SUM(amount), 0) as total FROM expenses WHERE date = ? GROUP BY currency ORDER BY currency",
        (today,),
    ).fetchall()
    conn.close()
    return {r["currency"]: r["total"] for r in rows}


def get_daily_summary(days: int = 7) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT date, currency, SUM(amount) as total, COUNT(*) as count FROM expenses GROUP BY date, currency ORDER BY date DESC LIMIT ?",
        (days * 3,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(expense_id: int) -> bool:
    conn = get_db()
    cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted


def get_monthly_stats(year_month: str) -> dict:
    """Return monthly stats: total by currency, favorite coffee, daily breakdown."""
    conn = get_db()
    currency_rows = conn.execute(
        "SELECT currency, COALESCE(SUM(amount), 0) as total, COUNT(*) as count FROM expenses WHERE strftime('%Y-%m', date) = ? GROUP BY currency",
        (year_month,),
    ).fetchall()

    fav_rows = conn.execute(
        "SELECT coffee_type, COUNT(*) as cnt FROM expenses WHERE strftime('%Y-%m', date) = ? AND coffee_type != '' GROUP BY coffee_type ORDER BY cnt DESC LIMIT 3",
        (year_month,),
    ).fetchall()

    daily_rows = conn.execute(
        "SELECT date, COUNT(*) as count, SUM(amount) as total FROM expenses WHERE strftime('%Y-%m', date) = ? AND currency = 'EUR' GROUP BY date ORDER BY date",
        (year_month,),
    ).fetchall()

    type_rows = conn.execute(
        "SELECT coffee_type, COUNT(*) as count, SUM(amount) as total FROM expenses WHERE strftime('%Y-%m', date) = ? AND currency = 'EUR' AND coffee_type != '' GROUP BY coffee_type ORDER BY count DESC",
        (year_month,),
    ).fetchall()

    conn.close()
    return {
        "by_currency": {r["currency"]: {"total": r["total"], "count": r["count"]} for r in currency_rows},
        "favorites": [{"type": r["coffee_type"], "count": r["cnt"]} for r in fav_rows],
        "daily": [dict(r) for r in daily_rows],
        "by_type": [{"type": r["coffee_type"], "count": r["count"], "total": r["total"]} for r in type_rows],
    }


def get_world_stats() -> dict:
    """Return world travel/coffee stats for the game."""
    conn = get_db()

    # Unique countries visited
    country_rows = conn.execute(
        """SELECT country, COUNT(*) as drink_count,
                  COUNT(DISTINCT location) as locations,
                  MIN(date) as first_visit, MAX(date) as last_visit,
                  GROUP_CONCAT(DISTINCT coffee_type) as coffee_types
           FROM expenses
           WHERE country != ''
           GROUP BY country
           ORDER BY drink_count DESC""",
    ).fetchall()

    # Total unique countries
    total_countries = conn.execute(
        "SELECT COUNT(DISTINCT country) as cnt FROM expenses WHERE country != ''"
    ).fetchone()["cnt"]

    # Total drinks
    total_drinks = conn.execute(
        "SELECT COUNT(*) as cnt FROM expenses"
    ).fetchone()["cnt"]

    # Countries with coordinates for map
    coord_rows = conn.execute(
        """SELECT country, location, latitude, longitude, coffee_type, date, notes
           FROM expenses
           WHERE latitude != 0 AND longitude != 0
           ORDER BY date DESC
           LIMIT 200""",
    ).fetchall()

    # Coffee passport — all countries sorted by first drink
    passport_rows = conn.execute(
        """SELECT country, MIN(date) as first_drink, COUNT(*) as total,
                  GROUP_CONCAT(DISTINCT coffee_type) as types
           FROM expenses WHERE country != ''
           GROUP BY country
           ORDER BY first_drink""",
    ).fetchall()

    conn.close()

    return {
        "countries": [dict(r) for r in country_rows],
        "total_countries": total_countries or 0,
        "total_drinks": total_drinks or 0,
        "coordinates": [dict(r) for r in coord_rows],
        "passport": [dict(r) for r in passport_rows],
    }


def upsert_coffee_country(country_code: str, country_name: str, flag_emoji: str = "", coffee_type: str = "", notes: str = "") -> int:
    """Add or update a country in the coffee passport."""
    conn = get_db()
    existing = conn.execute("SELECT id FROM coffee_countries WHERE country_code = ?", (country_code.upper(),)).fetchone()
    if existing:
        conn.execute(
            "UPDATE coffee_countries SET country_name = ?, flag_emoji = ?, coffee_type = ?, notes = ? WHERE country_code = ?",
            (country_name, flag_emoji, coffee_type, notes, country_code.upper()),
        )
        rowid = existing["id"]
    else:
        cur = conn.execute(
            "INSERT INTO coffee_countries (country_code, country_name, flag_emoji, coffee_type, notes) VALUES (?, ?, ?, ?, ?)",
            (country_code.upper(), country_name, flag_emoji, coffee_type, notes),
        )
        rowid = cur.lastrowid or 0
    conn.commit()
    conn.close()
    return rowid


def get_coffee_countries() -> list:
    """Get all countries in the coffee passport."""
    conn = get_db()
    rows = conn.execute("SELECT * FROM coffee_countries ORDER BY country_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]
