import sqlite3
import os
from pathlib import Path
from datetime import datetime

DB_PATH = Path("/app/data/kohvilogi.db")
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
            amount REAL NOT NULL,
            currency TEXT DEFAULT 'EUR',
            date TEXT NOT NULL,
            notes TEXT DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_expense(item: str, amount: float, currency: str = "EUR", date: str = None, notes: str = "") -> int:
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO expenses (item, amount, currency, date, notes, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (item, amount, currency, date, notes, datetime.now().isoformat()),
    )
    conn.commit()
    rowid = cur.lastrowid or 0
    conn.close()
    return rowid


def get_expenses(date: str = None, limit: int = 100) -> list:
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


def get_today_total() -> float:
    today = datetime.now().strftime("%Y-%m-%d")
    conn = get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE date = ? AND currency = 'EUR'",
        (today,),
    ).fetchone()
    conn.close()
    return row["total"] if row else 0.0


def get_daily_summary(days: int = 7) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT date, SUM(amount) as total, COUNT(*) as count FROM expenses WHERE currency = 'EUR' GROUP BY date ORDER BY date DESC LIMIT ?",
        (days,),
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
