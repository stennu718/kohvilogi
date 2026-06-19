"""Kohvilogi — FastAPI rakenduse seadistus."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.database import init_db
from app.routes import register_routes

# Rate limiter — IP-põhine
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Kohvilogi")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — lubatud originid (tühja puhul kõik — muuda tootmises)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tootmises: ["https://kohvilogi.example.com"]
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Andmebaasi initsialiseerimine
init_db()

# Endpoint'id
register_routes(app, templates)
