"""Kohvilogi — Global error handlers and middleware.

Provides consistent JSON error responses, request logging,
and centralized exception handling across the app.
"""

import traceback
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.logging_config import get_logger

logger = get_logger("kohvilogi.errors")


def register_error_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app.

    All handlers return a consistent JSON error response:
    {
        "success": false,
        "error": "Human-readable error message",
        "detail": { ... },  # optional extra context
        "status_code": 422,
    }
    """

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic/FastAPI validation errors with clear messages."""
        errors = []
        for err in exc.errors():
            field = " -> ".join(str(loc) for loc in err.get("loc", []))
            errors.append({
                "field": field,
                "message": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            })

        logger.warning(
            f"Validation error on {request.url.path}",
            extra={"extra_data": {"errors": errors}},
        )

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "Validation failed",
                "detail": errors,
                "status_code": 422,
            },
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """Handle 404 Not Found."""
        if request.url.path.startswith("/api/"):
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error": "Resource not found",
                    "detail": f"No route matches: {request.url.path}",
                    "status_code": 404,
                },
            )
        # For HTML routes, let default behavior apply
        from fastapi.responses import Response
        return Response(status_code=404, content="Not Found")

    @app.exception_handler(405)
    async def method_not_allowed_handler(request: Request, exc):
        """Handle 405 Method Not Allowed."""
        return JSONResponse(
            status_code=405,
            content={
                "success": False,
                "error": f"Method {request.method} not allowed",
                "detail": f"{request.method} {request.url.path} is not supported",
                "status_code": 405,
            },
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc):
        """Handle 500 Internal Server Error."""
        logger.error(
            f"Internal error: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": "An unexpected error occurred. Please try again later.",
                "status_code": 500,
            },
        )

    @app.exception_handler(Exception)
    async def catch_all_handler(request: Request, exc: Exception):
        """Catch-all for unhandled exceptions."""
        logger.error(
            f"Unhandled exception: {type(exc).__name__}: {exc}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "Internal server error",
                "detail": str(exc) if app.debug else "An unexpected error occurred",
                "status_code": 500,
            },
        )
