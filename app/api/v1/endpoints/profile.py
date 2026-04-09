from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import user
from app.services import profile_service

router = APIRouter()


@router.get("/", response_model=user.PrivateUsersResponse)
def read_user_me(current_user: User = Depends(deps.get_current_active_user)):
    return current_user


@router.post("/image")
async def save_and_update_profile_image(
    request: Request,
    image: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await profile_service.save_and_update_profile_image(
        image=image, user_id=current_user.id, db=db
    )


@router.delete("/image")
async def delete_profile_image(
    request: Request,
    current_user: User = Depends(deps.get_current_unlocked_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await profile_service.clear_profile_image(user_id=current_user.id, db=db)
