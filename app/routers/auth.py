from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from app.depedencies import SessionDep, CurrentUser
from app.models.models import User
from app.schemas.token import TokenResponse
from app.schemas.user import UserCreateRequest, UserResponse
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreateRequest, session: SessionDep):
    existing_user = session.exec(select(User).where(User.username == data.username)).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    user = User(
        username=data.username.strip(),
        hashed_password=hash_password(data.password.strip()),
        is_admin="admin" in data.username.strip().lower()
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    user: User | None = session.exec(select(User).where(User.username == form.username.strip())).first()

    if not user or not verify_password(form.password.strip(), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return TokenResponse(access_token=create_access_token(user.username))


@router.get("/me", response_model=UserResponse)
def me(user: CurrentUser):
    return user
