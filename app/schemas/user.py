from pydantic import BaseModel, Field


class UserCreateRequest(BaseModel):
    """User create request model. For User registration request"""
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserResponse(BaseModel):
    """User create response model. For User registration response"""
    id: int
    username: str
    is_admin: bool
