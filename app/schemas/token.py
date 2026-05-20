"""Pydantic schema for authentication token responses."""

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Access token returned from the login endpoint."""

    access_token: str
    token_type: str = 'bearer'
