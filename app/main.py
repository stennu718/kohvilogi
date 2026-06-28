"""Kohvilogi — FastAPI rakenduse seadistus.

World-class API with:
- API versioning (/api/v1/ prefix)
- JWT authentication (optional, env-configured)
- Structured logging with rotation
- Global error handlers
- CORS, CSRF, rate limiting
- Health checks with deep status
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.config import get_config
from app.logging_config import setup_logging, get_logger
from app.database import init_db
from app.routes import register_routes
from app.error_handlers import register_error_handlers

# Load configuration
config = get_config()

# Setup logging
logger = setup_logging(level=config.LOG_LEVEL, log_file=config.LOG_FILE)

# Rate limiter — IP-põhine
limiter = Limiter(key_func=get_remote_address, default_limits=[config.RATE_LIMIT_DEFAULT])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info(f"Starting {config.APP_NAME} v{config.APP_VERSION}")
    logger.info(f"Config: debug={config.DEBUG}, auth={config.AUTH_ENABLED}")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down gracefully")


app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    description="Kohvilogi — track your coffee around the world",
    lifespan=lifespan,
    docs_url="/api/docs" if config.DEBUG else None,
    redoc_url="/api/redoc" if config.DEBUG else None,
)

# Attach rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Session middleware for CSRF protection
app.add_middleware(SessionMiddleware, secret_key=config.SECRET_KEY)

# CORS — environment-based allowed origins
allowed_origins = config.ALLOWED_ORIGINS.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

# Register global error handlers
register_error_handlers(app)

# Templates
templates = Jinja2Templates(directory="templates")


# Health check endpoint (outside versioning — infrastructure level)
@app.get("/health")
async def health():
    """Deep health check with database connectivity test."""
    from app.database import get_db
    db_status = "ok"
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
        logger.error(f"Health check failed: {e}")

    return JSONResponse({
        "status": "ok" if db_status == "ok" else "error",
        "app": "kohvilogi",
        "version": config.APP_VERSION,
        "database": db_status,
        "auth_enabled": config.AUTH_ENABLED,
    })


# Auth endpoints (v1)
from fastapi import Form

@app.post("/api/v1/auth/register")
# @limiter.limit("5/minute")  # Removed: function has no request param
async def api_register(
    username: str = Form(...),
    password: str = Form(...),
):
    """Register a new user account."""
    from app.auth import create_user, authenticate_user, _USERS

    if not username or not password:
        return JSONResponse(
            {"success": False, "error": "Username and password are required"},
            status_code=400,
        )

    if len(username) < 3 or len(password) < 6:
        return JSONResponse(
            {"success": False, "error": "Username min 3 chars, password min 6 chars"},
            status_code=400,
        )

    if username in _USERS:
        return JSONResponse(
            {"success": False, "error": "Username already taken"},
            status_code=409,
        )

    user = create_user(username, password)
    token = __import__("app.auth", fromlist=["create_access_token"]).create_access_token(username)

    logger.info(f"User registered: {username}")
    return {
        "success": True,
        "message": "Registration successful",
        "token": token,
        "username": username,
    }


@app.post("/api/v1/auth/login")
# @limiter.limit("10/minute")  # Removed: function has no request param
async def api_login(
    username: str = Form(...),
    password: str = Form(...),
):
    """Authenticate and receive a JWT token."""
    from app.auth import authenticate_user, create_access_token

    if not username or not password:
        return JSONResponse(
            {"success": False, "error": "Username and password are required"},
            status_code=400,
        )

    user = authenticate_user(username, password)
    if not user:
        logger.warning(f"Failed login attempt for: {username}")
        return JSONResponse(
            {"success": False, "error": "Invalid credentials"},
            status_code=401,
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(username)
    logger.info(f"User logged in: {username}")
    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "username": username,
    }


# Route'ta põhiregisterimine (HTML + API v1 JSON)
register_routes(app, templates)


# API v1 info endpoint
@app.get("/api/v1")
# @limiter.limit("100/minute")  # Removed: function has no request param
async def api_v1_info():
    """API v1 information and available endpoints."""
    return {
        "version": "v1",
        "docs": "/api/docs" if config.DEBUG else None,
        "endpoints": {
            "GET /api/v1": "This info",
            "GET /api/v1/auth/login": "Login with username/password",
            "POST /api/v1/auth/register": "Register new account",
            "GET /api/v1/stats": "Dashboard statistics",
            "GET /api/v1/world": "World map data",
            "GET /api/v1/world/top3": "Top 3 coffees per country",
            "GET /api/v1/world/by-year": "Coffee by year",
            "POST /api/v1/expenses": "Add a coffee expense",
            "GET /api/v1/expenses": "List coffee expenses",
            "GET /api/v1/health": "Health check",
        },
        "auth": {
            "enabled": config.AUTH_ENABLED,
            "type": "Bearer JWT",
            "header": "Authorization: Bearer <token>",
        },
    }
