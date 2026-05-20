"""Pydantic schemas for hero request and response payloads."""

from pydantic import BaseModel, Field


class HeroCreateRequest(BaseModel):
    """Payload used to create a hero."""

    name: str = Field(min_length=3, max_length=50)
    level: int = Field(default=1, ge=1, le=100)
    power: str = Field(min_length=3, max_length=50)
    active: bool = True


class HeroUpdateRequest(BaseModel):
    """Payload used to update hero fields."""

    name: str = Field(..., min_length=3, max_length=50)
    level: int = Field(..., ge=1, le=100)
    power: str = Field(..., min_length=3, max_length=50)
    active: bool


class HeroResponse(BaseModel):
    """Hero data returned by the API."""

    id: int
    name: str
    level: int
    power: str
    active: bool
