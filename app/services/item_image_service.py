from typing import Dict

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequest, NotFound
from app.models.item import Item
from app.models.item_image import ItemImage
from app.tasks.images import delete_image_task, process_item_image_task
from app.utils.image import save_and_validate_raw_image

allowed_types = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


async def save_image(
    item_id: int, user_id: int, image: UploadFile, db: AsyncSession
) -> Dict:
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

    raw_path = await save_and_validate_raw_image(image)
    # Add raw processing function
    # Remove EXIF data and add resizing quality control etc...

    new_image = ItemImage(item_id=item_id)
    db.add(new_image)

    await db.commit()
    await db.refresh(new_image)

    process_item_image_task.delay(str(raw_path.absolute()), new_image.id)

    return {"message": "Image added successfully!"}


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

    if file_path is None:
        raise BadRequest("Wait till the processing of image!")

    await db.delete(image)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()

        raise BadRequest(f"DataBase Error: {e}")

    delete_image_task.delay(file_path)

    return {"message": f"Image {image_id} deleted successfully!"}
