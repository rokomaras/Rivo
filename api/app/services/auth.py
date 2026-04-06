from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user import create_user, get_user_by_email
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


def login(db: Session, email: str, password: str) -> Token:
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token({"sub": user.email})
    return Token(access_token=token)
