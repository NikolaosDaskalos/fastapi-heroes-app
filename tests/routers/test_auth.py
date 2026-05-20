from datetime import datetime, timezone

from fastapi import status
from jose import jwt

from app.config import get_settings
from app.schemas.token import TokenResponse
from app.schemas.user import UserResponse

USER_CREDENTIALS = {"username": "test_user", "password": "12345678"}
ADMIN_CREDENTIALS = {"username": "test_admin", "password": "12345678"}
UNKNOWN_USER_CREDENTIALS = {"username": "missing_user", "password": "12345678"}
INVALID_USER_CREDENTIALS = {"username": "ab", "password": "short"}
PADDED_USER_CREDENTIALS = {"username": "  test_user  ", "password": "  12345678  "}


class TestUserAuth:
    """Test Authentication endpoints"""

    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/auth/register",
            json=USER_CREDENTIALS,
        )

        assert response.status_code == status.HTTP_201_CREATED
        body = UserResponse.model_validate(response.json())
        assert body.username == "test_user"
        assert body.is_admin is False

    def test_register_admin(self, client):
        """Test admin registration"""
        response = client.post(
            "/auth/register",
            json=ADMIN_CREDENTIALS,
        )

        assert response.status_code == status.HTTP_201_CREATED
        body = UserResponse.model_validate(response.json())
        assert body.username == "test_admin"
        assert body.is_admin is True

    def test_register_user_strips_credentials(self, client):
        """Test user registration strips leading and trailing whitespace."""
        response = client.post(
            "/auth/register",
            json=PADDED_USER_CREDENTIALS,
        )

        assert response.status_code == status.HTTP_201_CREATED
        body = UserResponse.model_validate(response.json())
        assert body.username == "test_user"
        assert body.is_admin is False

        login_response = client.post(
            "/auth/login",
            data=USER_CREDENTIALS,
        )
        assert login_response.status_code == status.HTTP_200_OK

    def test_register_user_with_same_username(self, client, registered_user):
        """Test user registration with same username will fail"""
        response = client.post(
            "/auth/register",
            json=registered_user,
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == "Username already exists"

    def test_register_user_rejects_invalid_payload(self, client):
        """Test user registration with invalid body."""
        response = client.post(
            "/auth/register",
            json=INVALID_USER_CREDENTIALS,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_login_user(self, client, registered_user):
        """Test user login"""
        response = client.post("/auth/login", data=registered_user)
        assert response.status_code == status.HTTP_200_OK
        body = TokenResponse.model_validate(response.json())
        assert body.access_token
        settings = get_settings()
        payload = jwt.decode(
            body.access_token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        assert payload["sub"] == registered_user["username"]
        assert payload["exp"] > datetime.now(timezone.utc).timestamp()
        assert body.token_type == "Bearer"

    def test_login_user_strips_credentials(self, client):
        """Test user login strips leading and trailing whitespace."""
        register_response = client.post("/auth/register", json=USER_CREDENTIALS)
        assert register_response.status_code == status.HTTP_201_CREATED

        response = client.post(
            "/auth/login",
            data=PADDED_USER_CREDENTIALS,
        )

        assert response.status_code == status.HTTP_200_OK
        body = TokenResponse.model_validate(response.json())
        assert body.access_token

    def test_login_rejects_unknown_user(self, client):
        """Test user login with unknown username."""
        response = client.post(
            "/auth/login",
            data=UNKNOWN_USER_CREDENTIALS,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect username or password"

    def test_login_rejects_wrong_password(self, client, registered_user):
        """Test user login with wrong password."""
        credentials = {
            "username": registered_user["username"],
            "password": "wrong-password",
        }
        response = client.post(
            "/auth/login",
            data=credentials,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Incorrect username or password"

    def test_me_for_user(self, client, logged_in_user):
        """Test user me"""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_200_OK
        body = UserResponse.model_validate(response.json())
        assert body.username == logged_in_user["username"]
        assert body.is_admin is False

    def test_me_for_admin(self, client, logged_in_admin):
        """Test user me"""
        response = client.get("/auth/me")
        assert response.status_code == status.HTTP_200_OK
        body = UserResponse.model_validate(response.json())
        assert body.username == logged_in_admin["username"]
        assert body.is_admin is True

    def test_me_requires_authenticated_user(self, client):
        """Test user me without bearer token."""
        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_me_rejects_invalid_token(self, client):
        """Test user me with invalid bearer token."""
        client.headers.update({"Authorization": "Bearer invalid-token"})

        response = client.get("/auth/me")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json()["detail"] == "Could not validate credentials"
