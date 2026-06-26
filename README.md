# Kohvilogi

[![CI](https://github.com/stennu718/kohvilogi/actions/workflows/ci.yml/badge.svg)](https://github.com/stennu718/kohvilogi/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Description

**Kohvilogi** (Estonian for "Coffee Log") is a web application for tracking your coffee consumption. Log each cup, view detailed statistics, explore coffee culture around the world on an interactive map, and share your coffee journey with others.

## Features

- **Coffee Logging** — Record each coffee with type, amount, currency, location, country, and GPS coordinates
- **Statistics Dashboard** — Daily and monthly consumption stats, streak tracking, unique countries visited, and compass progress
- **World Map** — Interactive map visualizing coffee regions across 27 global areas
- **Coffee Passport** — Track which countries' coffee you've tried
- **Progressive Web App (PWA)** — Installable on mobile devices, works offline
- **QR Code Sharing** — Generate a QR code with a summary of your coffee journey to share with friends

## Screenshots

| Dashboard | Map | Stats |
|-----------|-----|-------|
| ![Dashboard](docs/screenshot-dashboard.png) | ![Map](docs/screenshot-map.png) | ![Stats](docs/screenshot-stats.png) |

## Quick Start

### Option 1: Direct (Recommended for development)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Option 2: Editable install

```bash
pip install -e .
uvicorn app.main:app --reload
```

### Option 3: Docker

```bash
docker build -t kohvilogi .
docker run -p 8000:8000 kohvilogi
```

The application will be available at `http://localhost:8000`.

## API Documentation

Interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI).

| Endpoint | Description |
|---|---|
| `GET /` | Homepage |
| `POST /add` | Add a coffee entry |
| `POST /delete/{id}` | Delete an entry |
| `GET /stats` | Monthly statistics |
| `GET /map` | World map view |
| `GET /api/streak` | Streak and quick stats |
| `GET /api/world` | World data for map |
| `GET /health` | Health check |

## Running Tests

```bash
pytest tests/ -v
```

## Tech Stack

- **Backend:** Python 3.11+, FastAPI
- **Database:** SQLite (via aiosqlite)
- **Frontend:** Jinja2 templates, PWA support
- **Build System:** Hatchling
- **Testing:** pytest with async support, coverage reporting
- **CI/CD:** GitHub Actions
- **Deployment:** Docker

## Project Structure

```
kohvilogi/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry point
│   ├── routes.py        # API route definitions
│   ├── database.py      # Database connection and queries
│   └── constants.py     # Application constants
├── templates/           # Jinja2 HTML templates
│   ├── index.html
│   ├── stats.html
│   └── world.html
├── tests/               # Test suite
│   ├── test_unit.py
│   ├── test_integration.py
│   ├── test_e2e.py
│   ├── test_security.py
│   └── conftest.py
├── scripts/             # CI/CD helper scripts
├── .github/workflows/   # GitHub Actions workflows
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── railway.toml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
