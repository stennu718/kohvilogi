"""CLI for kohvilogi."""
import re
import click
from kohvilogi.airtable_client import add_expense, get_today_expenses


def parse_input(text: str) -> tuple:
    """Parse input like 'latte 3.50€' or 'coffee 2.50 EUR' into (item, amount, currency)."""
    text = text.strip()
    # Match: item name + amount + optional currency
    m = re.match(r"^(.+?)\s+(\d+(?:\.\d+)?)\s*(€|EUR|USD|GBP)?$", text)
    if not m:
        raise ValueError(f"Cannot parse: '{text}'. Format: 'item amount [currency]'")
    item = m.group(1).strip()
    amount = float(m.group(2))
    currency = m.group(3) or "EUR"
    if currency == "€":
        currency = "EUR"
    return item, amount, currency


@click.group()
def main():
    """Kohvilogi - log expenses to Airtable."""
    pass


@main.command()
@click.argument("entry")
def log(entry):
    """Log an expense. Example: kohv log 'latte 3.50€'"""
    try:
        item, amount, currency = parse_input(entry)
        result = add_expense(item, amount, currency)
        click.echo(f"Logged: {item} {amount} {currency}")
    except ValueError as e:
        click.echo(f"Error: {e}", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
def today():
    """Show today's expenses."""
    try:
        records = get_today_expenses()
        if not records:
            click.echo("No expenses today.")
            return
        total = 0.0
        for r in records:
            f = r["fields"]
            amt = f.get("Amount", 0)
            total += amt
            click.echo(f"  {f.get('Item', '?')}  {amt} {f.get('Currency', 'EUR')}")
        click.echo(f"---\n  Total: {total:.2f} EUR")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == "__main__":
    main()
