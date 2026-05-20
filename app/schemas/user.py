"""Pydantic schemas for user registration and response payloads."""

from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """Payload used to register a new user."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """User data returned by the API without password details."""

    id: int
    username: str
    is_admin: bool
