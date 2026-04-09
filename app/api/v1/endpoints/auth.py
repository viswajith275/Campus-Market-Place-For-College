from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.config import settings
from app.core.security import create_token
from app.models.user import User
from app.schemas.user import PrivateUsersResponse, UserCreate
from app.services import user_service

router = APIRouter()


@router.post("/register")
async def create_user(
    request: Request, user_in: UserCreate, db: AsyncSession = Depends(deps.get_db)
):

    return await user_service.create_user(db, user_in)


@router.post("/login", response_model=PrivateUsersResponse)
async def login_user(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(deps.get_db),
):
    user = await user_service.authenticate_user(
        username=form_data.username, password=form_data.password, db=db
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password!",
        )

    token = await deps.create_refresh_token(db=db, user_id=user.id)

    access_token = create_token(
        user_id=user.id,
        token_type="access",
        expires_time=timedelta(minutes=settings.access_token_expire_minutes),
    )

    refresh_token = create_token(
        user_id=user.id,
        token_type="refresh",
        expires_time=timedelta(days=settings.refresh_token_expire_days),
        unique_id=str(token.id),
        secret=token.refresh_key,
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",  # change later
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",  # change later
    )

    return user


@router.post("/refresh")
async def refresh_tokens(
    request: Request, response: Response, db: AsyncSession = Depends(deps.get_db)
):

    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token is missing!"
        )

    user_id = await deps.validate_refresh_token(refresh_token=refresh_token, db=db)

    access_token = create_token(
        user_id=user_id,
        token_type="access",
        expires_time=timedelta(minutes=settings.access_token_expire_minutes),
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite="lax",
    )

    return {"message": "Token refreshed"}


@router.post("/logout")
async def logout_user(
    request: Request, response: Response, db: AsyncSession = Depends(deps.get_db)
):

    refresh_token = request.cookies.get("refresh_token")

    await deps.delete_refresh_token(refresh_token, db)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {"message": "Logged out successfully"}
