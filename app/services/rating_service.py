from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config import settings
from app.core.exceptions import BadRequest, NotFound
from app.models.enum import RatingStatus, TransactionStatus
from app.models.rating import Rating
from app.models.transaction import Transaction
from app.models.user import User


async def fetch_my_ratings(user_id: int, db: AsyncSession) -> Sequence[Rating]:
    result = await db.execute(
        select(Rating)
        .where(Rating.rater_id == user_id)
        .options(joinedload(Rating.rated_user))
    )
    ratings = result.scalars().all()

    if not ratings:
        raise NotFound("Ratings not found!")

    return ratings


async def update_rating(
    rating_id: int, user_id: int, score: float, db: AsyncSession
) -> Rating:

    result = await db.execute(
        select(Rating).where(
            Rating.id == rating_id,
            Rating.rater_id == user_id,
            Rating.status == RatingStatus.Pending,
        )
    )
    rating = result.scalar_one_or_none()

    if rating is None:
        raise NotFound("Rating not found!")

    if score > 5 or score < 1:
        raise BadRequest("Rating should be between 1-5")

    try:
        rating.score = score
        rating.status = RatingStatus.Completed

        result = await db.execute(
            select(Transaction).where(Transaction.id == rating.transaction_id)
        )
        transaction = result.scalar_one_or_none()

        if transaction is None:
            raise NotFound("Transaction not found!")

        transaction.status = TransactionStatus.Completed

        result = await db.execute(select(User).where(User.id == user_id))
        rater = result.scalar_one_or_none()

        if rater is None:
            raise NotFound("User not found!")

        rater.locked = False

        result = await db.execute(select(User).where(User.id == rating.rated_id))
        rated = result.scalar_one_or_none()

        if rated is None:
            raise NotFound("User not found!")

        if score < 5:
            penalty = (5 - score) * settings.bias_factor
            score = max(score - penalty, 1.0)

        rated.total_rating += score
        rated.rating = round(rated.total_rating / rated.transaction_count, 2)

        await db.commit()

        result = await db.execute(
            select(Rating)
            .where(Rating.id == rating_id)
            .options(joinedload(Rating.rated_user))
        )
        rating = result.scalar_one_or_none()

        if rating is None:
            raise NotFound("Error!")

    except Exception as e:
        await db.rollback()

        raise e

    return rating
