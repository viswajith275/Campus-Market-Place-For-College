from typing import List

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import item
from app.services import admin_service

router = APIRouter()


@router.get("/reported-items", response_model=List[item.AdminItemResponse])
async def fetch_feed(
    request: Request,
    current_user: User = Depends(deps.get_current_admin_user),
    db: AsyncSession = Depends(deps.get_db),
    skip: int = Query(default=0, ge=0, description="No of items to skip"),
    limit: int = Query(default=10, ge=1, le=50, description="No of items needed"),
):
    return await admin_service.fetch_feed(db=db, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=item.AdminUniqueItemResponse)
async def fetch_one_item(
    request: Request,
    item_id: int,
    current_user: User = Depends(deps.get_current_admin_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await admin_service.fetch_one_item(item_id=item_id, db=db)


@router.delete("/{item_id}")
async def delete_item(
    request: Request,
    item_id: int,
    current_user: User = Depends(deps.get_current_admin_user),
    db: AsyncSession = Depends(deps.get_db),
):

    return await admin_service.delete_item(
        item_id=item_id,
        db=db,
    )
