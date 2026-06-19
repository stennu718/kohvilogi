# Kohvilogi — Testid

## Käivitamine

```bash
# Kõik testid
pytest

# Coverage raport
pytest --cov --cov-report=term-missing

# Ainult kiired testid (välja jäetud slow)
pytest -m "not slow"

# Paralleelselt (kiirem)
pytest -n auto
```

## Struktuur

| Fail | Sisu |
|------|------|
| `conftest.py` | Ühised fikstuurid (`client`, `client_with_data`) |
| `factories.py` | Testandmete fabrikad (`make_coffee`, `make_expense_data`) |
| `test_app.py` | Olemasolevad testid (säilitatud) |
| `test_unit.py` | Ühiktestid (F2) |
| `test_integration.py` | Integratsioonitestid (F3) |
| `test_e2e.py` | E2E testid (F4) |
| `test_security.py` | Turvalisus- ja jõudlustestid (F5) |

## KPI-d

- Coverage ≥ 80%
- Kogu aeg < 15 min
- 0 kriitilist viga
