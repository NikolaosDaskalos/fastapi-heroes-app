from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """Access_token response model returned from login"""
    access_token: str
    token_type: str = 'bearer'
