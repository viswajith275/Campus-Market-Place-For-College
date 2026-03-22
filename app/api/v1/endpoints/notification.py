from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.user import User
from app.schemas import notification
from app.services import notification_service

router = APIRouter()


@router.get("/stream", include_in_schema=False)
async def stream_notifications(
    current_user: User = Depends(deps.get_current_active_user),
):
    return await notification_service.notification_generator(user_id=current_user.id)


@router.get("/", response_model=List[notification.NotificationResponse])
async def fetch_notifications(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await notification_service.fetch_notifications(
        user_id=current_user.id, db=db
    )


# for marking single notification as read

# @router.get("/{notification_id}", response_model=notification.NotificationResponse)
# async def mark_notification_read(
#    request: Request,
#    notification_id: int,
#    current_user: User = Depends(deps.get_current_active_user),
#    db: AsyncSession = Depends(deps.get_db),
# ):
#    return


@router.get("/read_all")
async def read_all_notifications(
    request: Request,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db),
):
    return await notification_service.mark_all_read(user_id=current_user.id, db=db)
