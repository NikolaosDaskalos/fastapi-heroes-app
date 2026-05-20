"""Pydantic schema for authentication token responses."""

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    """Access token returned from the login endpoint."""
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = 'Bearer'
