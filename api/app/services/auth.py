from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user import create_user, get_user_by_email, get_user_by_id
from app.schemas.auth import Token, UserCreate, UserRead


def register(db: Session, data: UserCreate) -> UserRead:
    existing = get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed = hash_password(data.password)
    user = create_user(db, email=data.email, hashed_password=hashed)
    return user


def login(db: Session, email: str, password: str) -> tuple[Token, str]:
    """Returns (Token, refresh_token_string)."""
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive",
        )
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token), refresh_token


def refresh(db: Session, refresh_token: str) -> tuple[Token, str]:
    """Validate refresh token, return new access + rotated refresh token."""
    from jose import JWTError

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = decode_refresh_token(refresh_token)
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = get_user_by_id(db, int(user_id))
    if user is None or not user.is_active:
        raise credentials_exception

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token({"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token), new_refresh
