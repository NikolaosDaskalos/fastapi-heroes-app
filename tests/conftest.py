"""Reusable pytest setup for FastAPI tests."""

import sys
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db import get_session
from app.main import app
from app.schemas.token import TokenResponse

USER_CREDENTIALS = {"username": "test_user", "password": "12345678"}
ADMIN_CREDENTIALS = {"username": "test_admin", "password": "12345678"}

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_session():
    """Use the temporary test database instead of the real app database."""
    with Session(test_engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(autouse=True)
def prepare_test_database():
    """Create a clean database for each test."""
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)
    yield
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture
def client():
    """FastAPI test client that uses the test database override."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def registered_user(client):
    credentials = USER_CREDENTIALS.copy()
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == status.HTTP_201_CREATED
    return credentials


@pytest.fixture
def registered_admin(client):
    credentials = ADMIN_CREDENTIALS.copy()
    response = client.post("/auth/register", json=credentials)
    assert response.status_code == status.HTTP_201_CREATED
    return credentials


def _login(client, credentials):
    response = client.post("/auth/login", data=credentials)
    assert response.status_code == status.HTTP_200_OK
    token = TokenResponse.model_validate(response.json())
    client.headers.update({"Authorization": f"Bearer {token.access_token}"})
    return credentials | token.model_dump()


@pytest.fixture
def logged_in_user(client, registered_user):
    return _login(client, registered_user)


@pytest.fixture
def logged_in_admin(client, registered_admin):
    return _login(client, registered_admin)
