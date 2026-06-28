"""Kohvilogi — Structured logging configuration.

Provides rotation, JSON formatting, and environment-aware log levels.
"""

import logging
import logging.handlers
import json
import sys
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    """Format log records as structured JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        exc_info = record.exc_info[0] if record.exc_info else None
        exc_msg = record.exc_info[1] if record.exc_info else None
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if exc_info and exc_msg:
            log_entry["exception"] = {
                "type": exc_info.__name__,
                "message": str(exc_msg),
            }

        # Add any extra fields
        extra_data = getattr(record, "extra_data", None)
        if extra_data:
            log_entry["extra"] = extra_data

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO", log_file: str = "") -> logging.Logger:
    """Configure application logging with console and optional file output.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to a log file for persistent storage

    Returns:
        Configured root logger for the app
    """
    logger = logging.getLogger("kohvilogi")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Avoid duplicate handlers on re-init
    logger.handlers.clear()

    # Console handler — human-readable in dev, JSON in production
    console_handler = logging.StreamHandler(sys.stdout)
    if level.upper() == "DEBUG":
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%H:%M:%S",
            )
        )
    else:
        console_handler.setFormatter(JSONFormatter())

    logger.addHandler(console_handler)

    # Optional rotating file handler
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "kohvilogi") -> logging.Logger:
    """Get a named logger instance."""
    return logging.getLogger(name)
