from typing import Dict, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, NotFound
from app.models.enum import ItemStatus, NotificationType
from app.models.item import Item
from app.models.report import Report
from app.services.notification_service import notify
from app.tasks.images import delete_image_task


async def fetch_feed(skip: int, limit: int, db: AsyncSession) -> Sequence[Item]:
    result = await db.execute(
        select(Item)
        .where(Item.status == ItemStatus.Active)
        .options(
            joinedload(Item.seller),
            selectinload(Item.images),
        )
        .order_by(
            select(func.count(Report.id))
            .where(Report.item_id == Item.id)
            .scalar_subquery()
            .desc()
        )
        .offset(skip)
        .limit(limit)
    )

    items = result.scalars().all()

    if not items:
        raise NotFound("No items found!")

    return items


async def fetch_one_item(item_id: int, db: AsyncSession) -> Item:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id)
        .options(
            joinedload(Item.seller),
            selectinload(Item.images),
            selectinload(Item.reports).joinedload(Report.reporter),
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found!")

    return item


async def delete_item(item_id: int, db: AsyncSession) -> Dict:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.status == ItemStatus.Active)
        .options(selectinload(Item.images))
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found!")

    item_title = item.title
    item_seller_id = item.seller_id
    file_path_to_delete = [image.image_path for image in item.images]

    await db.delete(item)

    try:
        await db.commit()
    except Exception as e:
        await db.rollback()

        raise BadRequest(f"Database error: {e}")

    for path in file_path_to_delete:
        delete_image_task.delay(path)

    notify(
        user_id=str(item_seller_id),
        title="Item deleted by admin",
        message=f"Item {item_title} deleted by admin due to uncompromisable practises!",
        type=NotificationType.Item_Deleted,
    )

    return {"message": f"Item {item_id} deleted successfully!"}
