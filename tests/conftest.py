"""Kohvilogi — ühised testfikstuurid ja -utiliidid."""

import os
import tempfile
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Loo puhas test client igale testile — eraldi ajutine andmebaas."""
    old_db = os.environ.get("DB_PATH")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    os.environ["DB_PATH"] = db_path

    import importlib
    import app.database
    importlib.reload(app.database)
    app.database.init_db()

    from app.main import app
    c = TestClient(app, follow_redirects=False)
    yield c

    # Puhasta
    if os.path.exists(db_path):
        os.unlink(db_path)
    if old_db:
        os.environ["DB_PATH"] = old_db
    else:
        os.environ.pop("DB_PATH", None)


@pytest.fixture
def client_with_data(client):
    """Test client näidisandmetega — 3 kohvi 2 riigis."""
    client.post("/add", data={
        "coffee_type": "Espresso", "amount": "3.50", "currency": "EUR",
        "notes": "Tallinn", "location": "Tallinn", "country": "EE",
        "latitude": "59.44", "longitude": "24.75",
    })
    client.post("/add", data={
        "coffee_type": "Latte", "amount": "4.00", "currency": "EUR",
        "notes": "Helsinki", "location": "Helsinki", "country": "FI",
        "latitude": "60.17", "longitude": "24.94",
    })
    client.post("/add", data={
        "coffee_type": "Cappuccino", "amount": "3.80", "currency": "EUR",
        "notes": "Tallinn", "location": "Tallinn", "country": "EE",
        "latitude": "59.44", "longitude": "24.75",
    })
    return client
