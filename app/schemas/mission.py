from pydantic import BaseModel, Field


class MissionCreateRequest(BaseModel):
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False
    hero_id: int = Field(ge=1)


class MissionUpdateRequest(BaseModel):
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False

class MissionResponse(BaseModel):
    id: int
    title: str
    difficulty: int
    completed: bool
    hero_id: int
