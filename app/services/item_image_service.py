import os
import uuid
from typing import Dict

import aiofiles
import aiofiles.os
import magic
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import BadRequest, NotFound
from app.models.item import Item
from app.models.item_image import ItemImage
from app.tasks.images import delete_image_task

allowed_types = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


async def save_image(
    item_id: int, user_id: int, image: UploadFile, db: AsyncSession
) -> ItemImage:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.seller_id == user_id)
        .options(selectinload(Item.images))
    )

    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found or you do not own this item!")

    if len(item.images) > 3:
        raise BadRequest("You have reached the limit for images!")

    if image.content_type not in allowed_types:
        raise BadRequest(
            f"Unsupported media type. Allowed: {allowed_types.keys}",
        )

    first_chunk = await image.read(2048)  # Read first 2KB to check headers
    actual_mime_type = magic.from_buffer(first_chunk, mime=True)

    if actual_mime_type not in allowed_types:
        raise BadRequest(
            f"Unsupported media type. Allowed: {allowed_types}",
        )

    await image.seek(0)

    extension_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
    file_extension = extension_map.get(actual_mime_type, ".bin")
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(f"app/{settings.upload_directory}", unique_filename)

    saved_bytes = 0
    try:
        async with aiofiles.open(file_path, "wb") as out_file:
            while content := await image.read(1024 * 1024):  # 1MB chunks
                saved_bytes += len(content)
                if saved_bytes > settings.max_image_size:
                    await aiofiles.os.remove(file_path)
                    raise BadRequest(
                        f"File exceeds maximum allowed size of {settings.max_image_size / 1024 / 1024}MB."
                    )
                await out_file.write(content)
    except Exception as e:
        raise e

    new_image = ItemImage(item_id=item_id, image_path=file_path)
    db.add(new_image)

    try:
        await db.commit()
        await db.refresh(new_image)

    except Exception as e:
        await db.rollback()

        if await aiofiles.os.path.exists(file_path):
            await aiofiles.os.remove(file_path)

        raise e

    return new_image


async def delete_image(image_id: int, user_id: int, db: AsyncSession) -> Dict:
    result = await db.execute(
        select(ItemImage)
        .join(Item)
        .where(Item.seller_id == user_id)
        .where(ItemImage.id == image_id)
    )

    image = result.scalar_one_or_none()

    if image is None:
        raise NotFound("Image not found!")

    file_path = image.image_path

    await db.delete(image)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()

        raise BadRequest(f"DataBase Error: {e}")

    delete_image_task.delay(file_path)

    return {"message": f"Image {image_id} deleted successfully!"}
