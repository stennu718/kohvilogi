# Kohvilogi

**Log coffee to the map & journal** — track your coffee consumption with statistics and world map visualization.

[![CI](https://github.com/stennu718/kohvilogi/actions/workflows/tests.yml/badge.svg)](https://github.com/stennu718/kohvilogi/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/github/v/release/stennu718/kohvilogi)](https://github.com/stennu718/kohvilogi/releases)

![Coffee Map](docs/screenshot.png)

## Features

- **Coffee logging** — record coffee type, amount, location, country, GPS coordinates
- **Statistics** — daily, weekly, monthly consumption analytics, streak tracking
- **World map** — interactive map with coffee regions (27 regions)
- **Coffee passport** — track which countries you've had coffee in
- **PWA support** — installable, offline-capable
- **Sharing** — QR code summary sharing

## Quick Start

```bash
# Clone
git clone https://github.com/stennu718/kohvilogi.git
cd kohvilogi

# Setup
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload
# Available at: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Homepage |
| `POST /add` | Add coffee entry |
| `POST /delete/{id}` | Delete entry |
| `GET /stats` | Monthly statistics |
| `GET /map` | World map data |
| `GET /api/streak` | Streak + quick stats |
| `GET /api/world` | World data |
| `GET /health` | Health check |

## Tech Stack

- **Backend:** FastAPI + SQLite
- **Frontend:** Jinja2 templates, PWA
- **Database:** SQLite (aiosqlite)
- **Deploy:** Docker

## Tests

```bash
pytest tests/ -v
```

## Screenshots

| Dashboard | Map | Stats |
|-----------|-----|-------|
| ![Dashboard](docs/screenshot-dashboard.png) | ![Map](docs/screenshot-map.png) | ![Stats](docs/screenshot-stats.png) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT
