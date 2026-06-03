"""Airtable client for kohvilogi."""
import os
import requests
from datetime import datetime

BASE_ID = os.environ.get("AIRTABLE_BASE_ID", "app3sftMPNl8N7w0m")
TABLE_NAME = "Expenses"


def _get_key():
    """Read Airtable API key from ~/.hermes/.env"""
    env_path = os.path.expanduser("~/.hermes/.env")
    with open(env_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith("AIRTABLE_API_KEY="):
                return stripped.split("=", 1)[1]
    raise RuntimeError("AIRTABLE_API_KEY not found in ~/.hermes/.env")


def _headers():
    return {
        "Authorization": f"Bearer {_get_key()}",
        "Content-Type": "application/json",
    }


def _table_id():
    """Get table ID by name."""
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    for t in resp.json()["tables"]:
        if t["name"] == TABLE_NAME:
            return t["id"]
    raise RuntimeError(f"Table '{TABLE_NAME}' not found in base {BASE_ID}")


def ensure_table():
    """Create Expenses table if it doesn't exist."""
    try:
        return _table_id()
    except RuntimeError:
        pass

    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    payload = {
        "name": TABLE_NAME,
        "fields": [
            {"name": "Item", "type": "singleLineText"},
            {"name": "Amount", "type": "number", "options": {"precision": 2}},
            {"name": "Currency", "type": "singleLineText"},
            {"name": "Date", "type": "date"},
            {"name": "Notes", "type": "multilineText"},
        ],
    }
    resp = requests.post(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()["id"]


def add_expense(item: str, amount: float, currency: str = "EUR", notes: str = ""):
    """Add an expense record to Airtable."""
    ensure_table()
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    payload = {
        "fields": {
            "Item": item,
            "Amount": amount,
            "Currency": currency,
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Notes": notes,
        }
    }
    resp = requests.post(url, headers=_headers(), json=payload)
    resp.raise_for_status()
    return resp.json()


def get_today_expenses() -> list:
    """Get today's expenses from Airtable."""
    ensure_table()
    today = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    params = {"filterByFormula": f"IS_SAME({{Date}}, '{today}')"}
    resp = requests.get(url, headers=_headers(), params=params)
    resp.raise_for_status()
    return resp.json().get("records", [])
