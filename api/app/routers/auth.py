from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.auth import LoginRequest, Token, UserCreate, UserRead
from app.services import auth as auth_service

router = APIRouter(prefix="/auth", tags=["auth"])

_REFRESH_COOKIE = "refresh_token"
_COOKIE_SECURE = False  # set True in production (HTTPS)


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_REFRESH_COOKIE,
        value=token,
        httponly=True,
        samesite="lax",
        secure=_COOKIE_SECURE,
        max_age=settings.JWT_REFRESH_EXPIRE_DAYS * 86400,
        path="/auth/refresh",
    )


@router.post("/register", response_model=UserRead, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register(db, data)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    token, refresh = auth_service.login(db, data.email, data.password)
    _set_refresh_cookie(response, refresh)
    return token


@router.post("/refresh", response_model=Token)
def refresh(
    response: Response,
    db: Session = Depends(get_db),
    refresh_token: str | None = Cookie(default=None, alias=_REFRESH_COOKIE),
):
    if not refresh_token:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )
    token, new_refresh = auth_service.refresh(db, refresh_token)
    _set_refresh_cookie(response, new_refresh)
    return token


@router.post("/logout", status_code=204)
def logout(response: Response):
    response.delete_cookie(key=_REFRESH_COOKIE, path="/auth/refresh")


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)):
    return current_user
