"""Pydantic schemas for mission request and response payloads."""

from pydantic import BaseModel, Field


class MissionCreateRequest(BaseModel):
    """Payload used to create a mission."""

    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False
    hero_id: int = Field(ge=1)


class MissionUpdateRequest(BaseModel):
    """Payload used to update mission fields."""

    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False


class MissionResponse(BaseModel):
    """Mission data returned by the API."""

    id: int
    title: str
    difficulty: int
    completed: bool
    hero_id: int
