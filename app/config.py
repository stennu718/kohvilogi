"""Kohvilogi — Application configuration classes.

Supports Development, Testing, and Production environments
with sensible defaults and environment variable overrides.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class BaseConfig:
    """Base configuration shared across all environments."""

    # App
    APP_NAME: str = "Kohvilogi"
    APP_VERSION: str = "0.3.0"
    DEBUG: bool = False
    TESTING: bool = False

    # Database
    DB_PATH: str = field(default_factory=lambda: os.getenv("DB_PATH", "/data/kohvilogi.db"))

    # Security
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "change-me-in-production"))
    ALLOWED_ORIGINS: str = field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "http://localhost:3000"))

    # Rate limiting
    RATE_LIMIT_DEFAULT: str = "100/minute"
    RATE_LIMIT_STORAGE_URL: str = field(default_factory=lambda: os.getenv("REDIS_URL", "memory://"))

    # Caching
    CACHE_TYPE: str = "memory"  # "memory" or "redis"
    CACHE_REDIS_URL: str = field(default_factory=lambda: os.getenv("REDIS_URL", ""))
    CACHE_DEFAULT_TIMEOUT: int = 300

    # Logging
    LOG_LEVEL: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    LOG_FILE: str = field(default_factory=lambda: os.getenv("LOG_FILE", ""))

    # Auth
    AUTH_ENABLED: bool = field(default_factory=lambda: os.getenv("AUTH_ENABLED", "false").lower() == "true")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 72


@dataclass
class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG: bool = True
    RATE_LIMIT_DEFAULT: str = "1000/minute"
    LOG_LEVEL: str = "DEBUG"


@dataclass
class TestingConfig(BaseConfig):
    """Testing configuration — fast, isolated, no auth."""
    TESTING: bool = True
    DB_PATH: str = ":memory:"
    RATE_LIMIT_DEFAULT: str = "10000/minute"
    AUTH_ENABLED: bool = False
    SECRET_KEY: str = "test-secret-key-not-for-production"
    LOG_LEVEL: str = "WARNING"


@dataclass
class ProductionConfig(BaseConfig):
    """Production configuration — strict, secure."""
    RATE_LIMIT_DEFAULT: str = "60/minute"
    CACHE_TYPE: str = "redis"
    LOG_LEVEL: str = "WARNING"


def get_config():
    """Return configuration based on FLASK_ENV / ENV environment variable."""
    env = os.getenv("ENV", os.getenv("FLASK_ENV", "development")).lower()
    configs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }
    return configs.get(env, DevelopmentConfig)()
