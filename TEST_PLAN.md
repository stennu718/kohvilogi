# Kohvilogi — Testimiseplaan

**Versioon:** 1.0
**Kuupäev:** 2026-06-19
**Projekt:** Kohvilogi v0.2.0 — FastAPI + SQLite + Tailwind PWA
**Repo:** y84312/kohvilogi (private)

---

## 1. Testimise ulatus (Scope)

### Testitakse
- Kõik API endpointid (`/`, `/add`, `/delete/{id}`, `/stats`, `/map`, `/api/stats`, `/api/world`, `/api/world/top3`, `/api/world/by-year`, `/api/share`, `/health`, `/manifest.json`, `/sw.js`)
- Andmebaasi operatsioonid (CRUD, päringud, aggregatsioonid)
- Valideerimisloogika (amount, currency, country, coffee_type)
- PWA komponendid (manifest, service worker)
- Turvalisus (SQL injection, XSS, piirangud)

### Ei testata
- Kolmandate osapoolte teenused (nt andmebaasi mootor ise)
- Brauseri renderdamist (E2E kasutab TestClient, mitte päist brauserit)
- Google Calendar sync (eraldi moodul, testitakse eraldi)

---

## 2. Teststrateegia

### Shift-Left lähenemine
- Testid kirjutatakse koos koodiga (TDD või kohe pärast)
- Iga PR peab läbima kõik testid enne merge'i
- Coverage > 80% — CI failib kui alla

### Test Pyramid 2.0
```
        /  E2E  \          ← 6 testi (tuumik)
       /----------\
      / Integration \     ← 21 testi (API + DB)
     /--------------\
    /   Unit Tests    \   ← 30+ testi (80%+ coverage)
   /--------------------\
  /  Security + Perf    \ ← 8 testi
 /------------------------\
```

### Testimise põhimõtted
- **Deklaratiivne** — kirjeldab mida testitakse, mitte kuidas
- **Iseseisev** — testid ei sõltu üksteisest (iga test = puhas DB)
- **Versioneeritud** — testid koodiga samas repos
- **Kiire** — kogu testisuite < 15 min

---

## 3. Keskkonnad

| Keskkond | Otstarve | Andmebaas |
|----------|----------|-----------|
| Test (pytest) | Iga test | Ajutine SQLite (tempfile) |
| CI (GitHub Actions) | Automaatne | Ajutine SQLite |
| Staging | Manuaalne test | Eraldi DB fail |
| Production | Mitte testitud | Tegelik DB |

**Andmehaldus:**
- Iga test kasutab eraldi ajutist andmebaasi (`tempfile`)
- Testandmeid genereeritakse factory'de abil
- Tootesandmeid EI kasutata testimiseks
- Puhas andmebaas tagab testide iseseisvuse

---

## 4. KPI-d ja mõõdikud

| Mõõdik | Eesmärk | Praegune | Seis |
|--------|---------|----------|------|
| Koodi katvus | ≥ 80% | ~15% | 🔴 |
| Defektide tihedus | < 1/1000 LOC | TBD | ⚪ |
| Testide arv (kokku) | 65+ | 25 | 🟡 |
| E2E testide arv | 6 | 0 | 🔴 |
| Testide täitmise aeg | < 15 min | ~5s | 🟢 |
| Kriitiliste vigade arv | 0 | TBD | ⚪ |

---

## 5. Exit / Entry kriteeriumid

### Testimise lõpetamine (Exit)
- ✅ Koodi katvus ≥ 80%
- ✅ 0 kriitilist viga (Critical/High)
- ✅ Kõik E2E testid läbitud
- ✅ Testide aeg < 15 min
- ✅ TEST_PLAN.md ajakohane

### Koodi produktsiooni viimine (Entry)
- ✅ Kõik testid roheline
- ✅ Coverage raport loodud
- ✅ Turvalisus testid läbitud
- ✅ Manuaalne QA läbitud (valitud teekonnad)

---

## 6. Defektide haldus

| Tase | Kirjeldus | SLA |
|------|-----------|-----|
| Critical | Andmekadu, turvaauk | < 1 tund |
| High | Peatsel katkestab | < 4 tundi |
| Medium | Töötab, kuid valesti | < 1 päev |
| Low | Kosmeetiline | < 1 nädal |

---

## 7. Testide struktuur

```
tests/
├── __init__.py
├── conftest.py          # Ühised fikstuurid, testandmehaldus
├── factories.py         # Testandmete fabrikad
├── test_app.py          # Olemasolevad testid (säilitada)
├── test_unit.py         # Ühiktestid (F2)
├── test_integration.py  # Integratsioonitestid (F3)
├── test_e2e.py          # E2E testid (F4)
├── test_security.py     # Turvalisus- ja jõudlustestid (F5)
└── README.md            # Kuidas käivitada
```

### Testcase'i struktuur
```python
class TestFeatureName:
    """Lühikirjeldus funktsioonist"""

    def test_scenario_expected_result(self, client):
        """ID.Nimi — mida testitakse"""
        # Arrange
        # Act
        # Assert
```

---

## 8. Ajakava

| Faas | Kirjeldus | Testide arv | Olek |
|------|-----------|-------------|------|
| F1 | Testimise alus (dokument, konfig, factory) | 0 | 🔴 Alustan |
| F2 | Ühiktestid | 30+ | ⚪ |
| F3 | Integratsioonitestid | 21+ | ⚪ |
| F4 | E2E testid | 6 | ⚪ |
| F5 | Turvalisus + jõudlus | 8 | ⚪ |
| F6 | CI/CD + aruandlus | 0 | ⚪ |
