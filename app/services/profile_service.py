from pathlib import Path
from typing import Dict

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequest, NotFound
from app.models.enum import ImageStatus
from app.models.user import User
from app.tasks.images import delete_image_task, process_profile_image_task
from app.utils.image import safe_remove, save_and_validate_raw_image


async def save_and_update_profile_image(
    user_id: int, image: UploadFile, db: AsyncSession
) -> Dict:
    result = await db.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()

    if user is None:
        raise NotFound("User not found!")

    prev_path = user.image_path

    if prev_path is not None:
        safe_remove(Path(prev_path))

    raw_path = await save_and_validate_raw_image(image)

    user.image_path = None
    user.image_status = ImageStatus.Pending

    await db.commit()

    process_profile_image_task.delay(str(raw_path.absolute()), user_id)

    return {"message": "Profile image updated successfully!"}


async def clear_profile_image(user_id: int, db: AsyncSession) -> Dict:
    result = await db.execute(select(User).where(User.id == user_id))

    user = result.scalar_one_or_none()

    if user is None:
        raise NotFound("User not found!")

    if user.image_status == ImageStatus.Pending:
        raise BadRequest("Image being processed try again after processing!")

    file_path = user.image_path

    delete_image_task.delay(file_path)

    user.image_path = None

    await db.commit()

    return {"message": "Profile image cleared successfully!"}
