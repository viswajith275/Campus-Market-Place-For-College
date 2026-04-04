from typing import List, Optional

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.enum import ItemCategory
from app.models.user import User
from app.schemas import item
from app.services import item_service

router = APIRouter()


@router.get("/feed", response_model=List[item.ItemResponse])
async def fetch_feed(
    request: Request,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(default=0, ge=0, description="No of items to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="No of items needed"),
):
    return await item_service.fetch_feed(db=db, skip=skip, limit=limit)


@router.get("/search", response_model=List[item.ItemResponse])
async def fetch_search_items(
    request: Request,
    search: Optional[str] = Query(None, min_length=3),
    categories: Optional[List[ItemCategory]] = Query(None),
    skip: int = Query(default=0, ge=0, description="No of items to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="No of items needed"),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_service.search_item(
        search_query=search, categories=categories, skip=skip, limit=limit, db=db
    )


@router.get("/bided-items", response_model=List[item.BidHistoryResponse])
async def fetch_my_bided_items(
    request: Request,
    skip: int = Query(default=0, ge=0, description="No of bids to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="No of bids needed"),
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_service.fetch_my_bided_items(
        skip=skip, limit=limit, user_id=current_user.id, db=db
    )


@router.get("/selled-items", response_model=List[item.ItemResponse])
async def fetch_my_items(
    request: Request,
    skip: int = Query(default=0, ge=0, description="No of items to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="No of items needed"),
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_service.fetch_my_selled_items(
        db=db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.get("/{item_id}", response_model=item.UniqueItemResponse)
async def fetch_one_item(
    request: Request,
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_service.fetch_one_item(item_id=item_id, db=db)


@router.post("/create", response_model=item.ItemResponse)
async def create_item(
    request: Request,
    item_request: item.ItemCreate,
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_service.create_item(
        item_request=item_request, user_id=current_user.id, db=db
    )


@router.patch("/{item_id}")
async def update_item(
    request: Request,
    item_id: int,
    item_patch: item.ItemUpdate,
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await item_service.update_item(
        item_updation_request=item_patch,
        item_id=item_id,
        user_id=current_user.id,
        db=db,
    )


@router.delete("/{item_id}")
async def delete_item(
    request: Request,
    item_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await item_service.delete_item(
        item_id=item_id,
        user_id=current_user.id,
        db=db,
    )
