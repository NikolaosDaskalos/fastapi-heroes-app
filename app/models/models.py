"""Database table models for users, heroes, and missions."""

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    """Application user with login credentials and admin flag."""

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_admin: bool = False


class Hero(SQLModel, table=True):
    """Hero entity that can be assigned to missions."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, min_length=3)
    power: str = Field(min_length=3)
    level: int = Field(default=1, ge=1, le=100)
    active: bool = True


class Mission(SQLModel, table=True):
    """Mission entity linked to the hero responsible for completing it."""

    id: int = Field(default=None, primary_key=True)
    title: str = Field(min_length=5)
    difficulty: int = Field(ge=1, le=10)
    completed: bool = False
    hero_id: int = Field(foreign_key="hero.id")
