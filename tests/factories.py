"""Kohvilogi — testandmete fabrikad.

Kasutamine:
    from tests.factories import make_coffee, make_expense_data

    expense = make_coffee(client, country="EE")
    data = make_expense_data(coffee_type="Latte", amount="4.00")
"""

from typing import Any


def make_expense_data(
    coffee_type: str = "Espresso",
    amount: str = "3.50",
    currency: str = "EUR",
    notes: str = "",
    location: str = "",
    country: str = "",
    latitude: str = "0",
    longitude: str = "0",
) -> dict[str, str]:
    """Loo POST /add vormi andmed — deklaratiivne, taaskasutatav."""
    return {
        "coffee_type": coffee_type,
        "amount": amount,
        "currency": currency,
        "notes": notes,
        "location": location,
        "country": country,
        "latitude": latitude,
        "longitude": longitude,
    }


def make_coffee(
    client,
    coffee_type: str = "Espresso",
    amount: str = "3.50",
    currency: str = "EUR",
    country: str = "",
    location: str = "",
    latitude: str = "0",
    longitude: str = "0",
) -> dict[str, Any]:
    """Lisa kohv läbi API ja tagasta vastus."""
    data = make_expense_data(
        coffee_type=coffee_type,
        amount=amount,
        currency=currency,
        country=country,
        location=location,
        latitude=latitude,
        longitude=longitude,
    )
    r = client.post("/add", data=data)
    assert r.status_code in (302, 303), f"make_coffee failed: {r.status_code}"
    return r


def make_multiple_coffees(client, count: int = 5, country: str = "EE") -> list:
    """Lisa mitu kohvi järjest — streak'i ja statistika testimiseks."""
    results = []
    for i in range(count):
        r = make_coffee(
            client,
            coffee_type="Espresso",
            amount=str(3.0 + i * 0.5),
            country=country,
        )
        results.append(r)
    return results
