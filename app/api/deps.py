import secrets
from datetime import datetime, timedelta
from typing import Annotated, AsyncGenerator

import jwt
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFound, UnAuthorized
from app.db.session import AsyncSessionLocal
from app.models.enum import UserRole
from app.models.token import UserToken
from app.models.user import User


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


# Fromating the token
async def get_token_from_cookie(request: Request) -> str:

    token = request.cookies.get("access_token")

    if not token:
        raise UnAuthorized("Not authenticated")

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    return token


# decoding and verifying the jwt token
async def get_current_user(
    token: Annotated[str, Depends(get_token_from_cookie)],
    db: AsyncSession = Depends(get_db),
) -> User | None:

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id = payload.get("uid")

        if user_id is None or payload.get("type") != "access":
            raise UnAuthorized(
                "Token invalid or expired",
            )

        result = await db.execute(select(User).where(User.id == user_id))

        return result.scalars().first()

    except Exception as e:
        raise e


# checking the user is not banned or revoked by the admin
async def get_current_active_user(
    current_user: Annotated[User | None, Depends(get_current_user)],
) -> User:
    if current_user is None:
        raise NotFound("User not found!")

    if current_user.disabled:
        raise UnAuthorized("Inactive user")

    return current_user


async def get_current_unlocked_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.locked:
        raise UnAuthorized(
            "Complete pending ratings first!",
        )

    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    if current_user.role == UserRole.User:
        raise UnAuthorized("You are not admin!")

    return current_user


async def validate_refresh_token(refresh_token: str, db: AsyncSession) -> int:
    try:
        payload = jwt.decode(
            refresh_token, settings.secret_key, algorithms=[settings.algorithm]
        )

        token_type = payload.get("type")
        secret = payload.get("secret")
        user_id = payload.get("uid")

        if user_id is None:
            raise NotFound("User not found!")

        if token_type != "refresh":
            raise UnAuthorized(
                f"Invalid Token {token_type}",
            )

        token_id = int(payload.get("jti"))  # type: ignore
        result = await db.execute(
            select(UserToken).where(
                UserToken.id == token_id, UserToken.user_id == user_id
            )
        )

        token = result.scalars().first()

        if not token or token.refresh_key != secret:
            # token may be stolen
            raise UnAuthorized(
                "Token revoked or Invalid",
            )

        return user_id
    except Exception as e:
        raise UnAuthorized(str(e))


async def delete_refresh_token(refresh_token: str | None, db: AsyncSession) -> None:
    if refresh_token:
        payload = jwt.decode(
            refresh_token, settings.secret_key, algorithms=[settings.algorithm]
        )

        token_id = int(payload.get("jti"))  # type: ignore

        result = await db.execute(select(UserToken).where(UserToken.id == token_id))

        token = result.scalar_one_or_none()

        if token is not None:
            await db.delete(token)
            await db.commit()


async def create_refresh_token(db: AsyncSession, user_id: int) -> UserToken:

    session_secret = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    token = UserToken(
        user_id=user_id, expires_at=expires_at, refresh_key=session_secret
    )

    db.add(token)
    await db.commit()
    await db.refresh(token)

    return token
