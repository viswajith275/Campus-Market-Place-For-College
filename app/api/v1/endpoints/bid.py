from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import bid
from app.services import bid_service

router = APIRouter()


@router.post("/{item_id}", response_model=bid.BidResponse)
async def create_bid(
    request: Request,
    item_id: int,
    bid_request: bid.BidCreate,
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await bid_service.create_bid(
        item_id=item_id, bid_request=bid_request, user_id=current_user.id, db=db
    )


@router.patch("/{bid_id}", response_model=bid.BidResponse)
async def update_bid(
    request: Request,
    bid_id: int,
    bid_patch: bid.BidUpdate,
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await bid_service.update_bid(
        bid_id=bid_id, bid_patch=bid_patch, user_id=current_user.id, db=db
    )


@router.delete("/{bid_id}")
async def delete_bid(
    request: Request,
    bid_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await bid_service.delete_bid(bid_id=bid_id, user_id=current_user.id, db=db)
