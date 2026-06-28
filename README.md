# Kohvilogi

Track your coffee drinking and see it on a world map.
Log what you drink, where you are, and discover your coffee habits.

**For**: Coffee lovers who want to understand their caffeine intake.

## Try it
[Link to live demo]

## How to use
1. Open the app
2. Click "Add Coffee"
3. Choose your coffee type and location
4. View your stats and world map

## Features
- Log coffee type, location, and notes
- World map showing where you've drunk coffee
- Statistics: daily/weekly/monthly consumption
- Export to CSV
- Works on mobile and desktop

## Screenshot
![Coffee Map](docs/screenshot.png)

## Technical Highlights

- **Backend**: Python 3.11 + Flask + SQLAlchemy
- **Auth**: JWT authentication with token blacklisting
- **Rate limiting**: Per-endpoint limits with Redis fallback
- **Testing**: 127 tests (unit, integration, e2e)
- **Security**: CORS, input validation, bcrypt hashing
- **Deployment**: Docker support, GitHub Actions CI/CD

## Architecture

```
app/
  routes.py       # API endpoints (auth, coffee, stats)
  auth.py         # JWT authentication and user management
  config.py       # App configuration (Dev/Test/Prod)
  schemas.py      # Request/response validation
  error_handlers.py # Global exception handling
  logging_config.py # Structured logging
  database.py     # Database connection and session management
main.py           # App entry point, middleware setup
```

## License
MIT
