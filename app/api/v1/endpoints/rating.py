from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import rating
from app.services import rating_service

router = APIRouter()


@router.get("/my_ratings", response_model=List[rating.RatingResponse])
async def fetch_my_ratings(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await rating_service.fetch_my_ratings(user_id=current_user.id, db=db)


@router.get("/{rating_id}/{score}", response_model=rating.RatingResponse)
async def update_rating(
    request: Request,
    rating_id: int,
    score: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await rating_service.update_rating(
        rating_id=rating_id, user_id=current_user.id, score=score, db=db
    )
