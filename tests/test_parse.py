"""Tests for kohvilogi parser."""
import pytest
from kohvilogi.cli import parse_input


def test_parse_simple():
    item, amount, currency = parse_input("latte 3.50€")
    assert item == "latte"
    assert amount == 3.50
    assert currency == "EUR"


def test_parse_eur():
    item, amount, currency = parse_input("coffee 2.50 EUR")
    assert item == "coffee"
    assert amount == 2.50
    assert currency == "EUR"


def test_parse_no_currency():
    item, amount, currency = parse_input("lunch 12.50")
    assert item == "lunch"
    assert amount == 12.50
    assert currency == "EUR"


def test_parse_multi_word():
    item, amount, currency = parse_input("cappuccino with oat milk 4.50€")
    assert item == "cappuccino with oat milk"
    assert amount == 4.50


def test_parse_usd():
    item, amount, currency = parse_input("book 15.99 USD")
    assert item == "book"
    assert amount == 15.99
    assert currency == "USD"


def test_parse_invalid():
    with pytest.raises(ValueError):
        parse_input("no amount here")
