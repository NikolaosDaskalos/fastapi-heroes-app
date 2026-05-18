from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from sqlmodel import Session, select
from starlette import status
from app.db import get_session
from app.config import get_settings
from app.models.models import User
from jose import JWTError

settings = get_settings()

# --- Database Session ---

SessionDep = Annotated[Session, Depends(get_session)]

# --- Authentication ---

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )

    return current_user


CurrentAdmin = Annotated[User, Depends(get_current_admin)]


# --- Pagination ---


def pagination(skip: int = 0, limit: int = 20) -> dict:
    """Reusable pagination dependency."""
    return {"skip": skip, "limit": limit}


Page = Annotated[dict, Depends(pagination)]
