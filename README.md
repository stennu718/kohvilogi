# Kohvilogi

CLI expense tracker - log coffee (or anything) to Airtable.

## Usage

```bash
kohv log "latte 3.50€"
kohv log "coffee 2.50 EUR"
kohv log "lunch 12.50"
kohv today
```

## Setup

```bash
pip install -e .
export AIRTABLE_BASE_ID=app3sftMPNl8N7w0m
```

Airtable API key is read from `~/.hermes/.env`.
