"""Kohvilogi — Request validation schemas using Pydantic.

Provides type-safe, validated input models for all API endpoints.
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.constants import VALID_COFFEE_TYPES, VALID_COUNTRIES


class ExpenseCreateSchema(BaseModel):
    """Schema for creating a new coffee expense entry."""

    model_config = ConfigDict(str_strip_whitespace=True)

    coffee_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Type of coffee consumed",
        examples=["Espresso"],
    )
    amount: float = Field(
        ...,
        gt=0,
        le=99999,
        description="Amount paid",
        examples=[3.50],
    )
    currency: str = Field(
        default="EUR",
        max_length=3,
        description="ISO 4217 currency code",
    )
    notes: str = Field(
        default="",
        max_length=500,
        description="Optional notes about the coffee",
    )
    location: str = Field(
        default="",
        max_length=200,
        description="Location where the coffee was consumed",
    )
    country: str = Field(
        default="",
        max_length=2,
        description="ISO 3166-1 alpha-2 country code",
    )
    latitude: float = Field(
        default=0.0,
        ge=-90,
        le=90,
        description="Latitude of the location",
    )
    longitude: float = Field(
        default=0.0,
        ge=-180,
        le=180,
        description="Longitude of the location",
    )

    @field_validator("coffee_type")
    @classmethod
    def validate_coffee_type(cls, v: str) -> str:
        """Ensure coffee type is from the allowed list."""
        normalized = v.lower().strip()
        if normalized not in VALID_COFFEE_TYPES:
            raise ValueError(
                f"Invalid coffee type: {v!r}. "
                f"Allowed types: {', '.join(sorted(VALID_COFFEE_TYPES))}"
            )
        return normalized

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Ensure country code is valid."""
        stripped = v.strip().upper()
        if not stripped:
            return ""
        if stripped not in VALID_COUNTRIES:
            raise ValueError(
                f"Invalid country code: {v!r}. "
                f"Must be a valid ISO 3166-1 alpha-2 code."
            )
        return stripped

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Normalize currency to uppercase."""
        return v.upper()


class YearMonthSchema(BaseModel):
    """Schema for year-month query parameter validation."""

    month: str = Field(
        default="",
        pattern=r"^\d{4}-\d{2}$",
        description="Year-month in YYYY-MM format",
    )


class APIResponse(BaseModel):
    """Standard API response wrapper."""

    success: bool = True
    message: str = ""
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""

    success: bool = False
    error: str = ""
    detail: Optional[str] = None
    status_code: int = 400
