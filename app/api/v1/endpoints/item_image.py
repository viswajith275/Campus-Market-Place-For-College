from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas.item_image import ItemImageResponse
from app.services import item_image_service

router = APIRouter()


@router.post("/{item_id}", response_model=ItemImageResponse)
async def create_image(
    request: Request,
    item_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_image_service.save_image(
        item_id=item_id, user_id=current_user.id, image=image, db=db
    )


@router.delete("/{image_id}")
async def delete_image(
    request: Request,
    image_id: int,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await item_image_service.delete_image(
        image_id=image_id, user_id=current_user.id, db=db
    )
