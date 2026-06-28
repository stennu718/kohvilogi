"""Kohvilogi — Authentication and authorization.

Provides optional JWT-based API authentication with Flask-Login-style session auth.
When AUTH_ENABLED is true, all /api/ endpoints require a valid JWT token.

Token format: Bearer <JWT> in Authorization header.
"""

import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Request, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.config import get_config
from app.logging_config import get_logger

logger = get_logger("kohvilogi.auth")

# Simple in-memory user store (use a real DB in production)
_USERS: dict[str, dict] = {}


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Hash a password with PBKDF2-SHA256 and random salt.

    Returns:
        Tuple of (hash_hex, salt_hex)
    """
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return dk.hex(), salt


def create_user(username: str, password: str) -> dict:
    """Create a new user with hashed password.

    Returns:
        User dict with username and password_hash (but NOT the plaintext password).
    """
    pw_hash, salt = hash_password(password)
    user = {
        "username": username,
        "password_hash": pw_hash,
        "salt": salt,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "is_active": True,
    }
    _USERS[username] = user
    logger.info(f"User '{username}' created", extra={"extra_data": {"username": username}})
    return user


def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Verify credentials and return user dict if valid.

    Returns:
        User dict if credentials match, None otherwise.
    """
    user = _USERS.get(username)
    if not user:
        # Constant-time fake check to prevent user enumeration
        hash_password(password, "fake-salt-for-timing")
        return None

    pw_hash, _ = hash_password(password, user["salt"])
    if not hmac.compare_digest(pw_hash, user["password_hash"]):
        return None

    return user


def _create_token(payload: dict, secret: str, expires_hours: int = 72) -> str:
    """Create a simple manual JWT-like token (no external deps).

    Format: base64(header).base64(payload).base64(signature)
    """
    import hashlib
    import json
    import base64

    header = {"alg": "HS256", "typ": "JWT"}
    now = datetime.now(timezone.utc)
    payload.update({
        "iat": now.isoformat(),
        "exp": (now + timedelta(hours=expires_hours)).isoformat(),
    })

    segments = f"{_b64url(json.dumps(header))}.{_b64url(json.dumps(payload))}"
    sig = hmac.new(secret.encode(), segments.encode(), hashlib.sha256).digest()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()

    return f"{segments}.{sig_b64}"


def _b64url(data: str) -> str:
    """Base64url encode without padding."""
    import base64
    return base64.urlsafe_b64encode(data.encode()).rstrip(b"=").decode()


def _decode_token(token: str, secret: str) -> Optional[dict]:
    """Verify a token and return its payload, or None if invalid."""
    import json
    import base64

    parts = token.split(".")
    if len(parts) != 3:
        return None

    header_b64, payload_b64, sig_b64 = parts

    # Verify signature
    expected_sig = hmac.new(
        secret.encode(), f"{header_b64}.{payload_b64}".encode(), hashlib.sha256
    ).digest()
    actual_sig = base64.urlsafe_b64decode(sig_b64 + "==")

    if not hmac.compare_digest(expected_sig, actual_sig):
        return None

    # Decode payload
    # Add padding back
    padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
    try:
        payload = json.loads(base64.urlsafe_b64decode(padded))
    except Exception:
        return None

    # Check expiration
    exp_str = payload.get("exp")
    if exp_str:
        try:
            exp = datetime.fromisoformat(exp_str)
            if datetime.now(timezone.utc) > exp:
                return None
        except ValueError:
            return None

    return payload


def create_access_token(username: str) -> str:
    """Create a JWT access token for the given username."""
    config = get_config()
    payload = {"sub": username}
    return _create_token(payload, config.SECRET_KEY, config.JWT_EXPIRATION_HOURS)


async def require_auth(request: Request) -> dict:
    """Dependency that enforces JWT authentication on API endpoints.

    Returns the decoded token payload.

    Raises:
        HTTPException: 401 if no token or invalid token
    """
    config = get_config()

    if not config.AUTH_ENABLED:
        return {"sub": "anonymous", "auth_disabled": True}

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        logger.warning("Missing or malformed Authorization header")
        raise HTTPException(
            status_code=401,
            detail="Missing or malformed Authorization header. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header[7:]  # Strip "Bearer "
    payload = _decode_token(token, config.SECRET_KEY)

    if payload is None:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user still exists
    username = payload.get("sub")
    if username and username not in _USERS:
        logger.warning(f"Token for non-existent user: {username}")
        raise HTTPException(
            status_code=401,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


def auth_response(error: str, status_code: int = 401) -> JSONResponse:
    """Create a standardized auth error response."""
    return JSONResponse(
        {"success": False, "error": error, "status_code": status_code},
        status_code=status_code,
        headers={"WWW-Authenticate": "Bearer"},
    )


# Create a default admin user on startup from env vars
def _setup_default_user():
    """Create a default admin user if ADMIN_USER and ADMIN_PASS are set."""
    username = os.getenv("ADMIN_USER", "")
    password = os.getenv("ADMIN_PASS", "")
    if username and password and username not in _USERS:
        create_user(username, password)
        logger.info(f"Default admin user '{username}' created from environment")


# Call on import (idempotent)
_setup_default_user()
