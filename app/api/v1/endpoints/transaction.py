from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import transaction
from app.services import transaction_service

router = APIRouter()


@router.get(
    "/my_selled_transactions",
    response_model=List[transaction.SellerTransactionResponse],
)
async def fetch_seller_transaction(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await transaction_service.fetch_my_selled_transactions(
        user_id=current_user.id, db=db
    )


@router.get(
    "/my_buyed_transactions", response_model=List[transaction.BuyerTransactionResponse]
)
async def fetch_buyed_transaction(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await transaction_service.fetch_my_buyed_transactions(
        user_id=current_user.id, db=db
    )


@router.post(
    "/{item_id}/{bid_id}", response_model=transaction.SellerTransactionResponse
)
async def create_transaction(
    request: Request,
    item_id: int,
    bid_id: int,
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await transaction_service.create_transaction(
        item_id=item_id, bid_id=bid_id, user_id=current_user.id, db=db
    )
