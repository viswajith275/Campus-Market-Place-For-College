from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.exceptions import Conflict
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


async def get_by_email(db: AsyncSession, email: str) -> User | None:

    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_by_username(db: AsyncSession, username: str) -> User | None:

    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> Dict[str, str]:

    if await get_by_email(db, user_in.email):
        raise Conflict(message=f"user with email {user_in.email} already exists!")

    if await get_by_username(db, user_in.username):
        raise Conflict(message=f"User with usernaem {user_in.username} already exists!")

    hashed_pasword = get_password_hash(user_in.password)

    user_obj = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hashed_pasword,
        phone_no=user_in.phone_no,
    )

    db.add(user_obj)
    await db.commit()
    await db.refresh(user_obj)

    return {"message": "User created successfully!"}


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:

    user = await get_by_username(db, username)

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user
