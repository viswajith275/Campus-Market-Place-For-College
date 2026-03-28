from typing import Dict, List, Optional, Sequence

from sqlalchemy import ARRAY, Enum, cast, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, NotFound
from app.models.bid import Bid
from app.models.enum import ItemCategory, ItemStatus, NotificationType
from app.models.item import Item
from app.models.report import Report
from app.schemas.item import ItemCreate, ItemUpdate
from app.schemas.report import ReportCreate
from app.services.notification_service import notify
from app.tasks.images import delete_image_task


async def fetch_feed(skip: int, limit: int, db: AsyncSession) -> Sequence[Item]:
    result = await db.execute(
        select(Item)
        .where(Item.status == ItemStatus.Active)
        .options(joinedload(Item.seller), selectinload(Item.images))
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    items = result.scalars().all()

    if not items:
        raise NotFound("No items found!")

    return items


async def fetch_my_selled_items(
    skip: int, limit: int, user_id: int, db: AsyncSession
) -> Sequence[Item]:
    result = await db.execute(
        select(Item)
        .where(Item.seller_id == user_id)
        .options(
            joinedload(Item.seller),
            selectinload(Item.images),
        )
        .order_by(Item.created_at.desc())
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
            selectinload(Item.bids).joinedload(Bid.bider),
        )
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found!")

    return item


async def fetch_my_bided_items(
    skip: int, limit: int, user_id: int, db: AsyncSession
) -> Sequence[Item]:
    result = await db.execute(
        select(Item)
        .join(Bid)
        .where(Bid.bider_id == user_id)
        .options(
            joinedload(Item.seller),
            selectinload(Item.images),
            selectinload(Item.bids),
        )
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()

    if not items:
        raise NotFound("No items found!")

    return items


async def search_item(
    search_query: Optional[str],
    categories: Optional[List[ItemCategory]],
    skip: int,
    limit: int,
    db: AsyncSession,
) -> Sequence[Item]:
    stmt = select(Item)

    if categories is not None:
        stmt = stmt.where(
            Item.categories.contains(
                cast(
                    [c.value for c in categories],
                    ARRAY(Enum(ItemCategory, name="itemcategories")),
                )
            )
        )

    if search_query is not None:
        query = search_query.strip()
        tsquery_input = " & ".join(f"{word}:*" for word in query.split())
        stmt = stmt.where(
            Item.search_vector.op("@@")(func.to_tsquery("english", tsquery_input))
        )

    result = await db.execute(
        stmt.options(
            joinedload(Item.seller),
            selectinload(Item.images),
        )
        .order_by(Item.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = result.scalars().all()

    if not items:
        raise NotFound("Item not found!")

    return items


async def create_item(item_request: ItemCreate, user_id: int, db: AsyncSession) -> Item:

    new_item = Item(
        seller_id=user_id,
        title=item_request.title,
        description=item_request.description,
        min_price=item_request.min_price,
        quantity=item_request.quantity,
        condition=item_request.condition,
        categories=item_request.categories,
    )

    db.add(new_item)
    await db.commit()

    result = await db.execute(
        select(Item)
        .where(Item.id == new_item.id)
        .options(
            joinedload(Item.seller),
            selectinload(Item.images),
        )
    )

    new_item = result.scalar_one_or_none()

    if new_item is None:
        raise NotFound("Error!")

    notify(
        user_id=str(user_id),
        title="Item created successfully",
        message=f"{new_item.title} has been created for {new_item.min_price} rupees",
        type=NotificationType.Item_Created,
    )

    return new_item


async def update_item(
    item_updation_request: ItemUpdate,
    item_id: int,
    user_id: int,
    db: AsyncSession,
) -> Item:
    patch_data = item_updation_request.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to Update!")

    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.seller_id == user_id)
        .options(
            joinedload(Item.seller),
            selectinload(Item.images),
        )
    )

    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not Found!")

    result = await db.execute(select(exists().where(Bid.item_id == item_id)))
    existing_bid = result.scalar()

    if existing_bid and patch_data.get("quantity", None) is not None:
        raise BadRequest("You cannot update quantity after someone places a bid!")

    for key, value in patch_data.items():
        setattr(item, key, value)

    await db.commit()

    notify(
        user_id=str(user_id),
        title="Item updated successfully",
        message="Item updated successfully",
        type=NotificationType.Item_Updated,
    )

    return item


async def delete_item(item_id: int, user_id: int, db: AsyncSession) -> Dict:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.seller_id == user_id)
        .options(selectinload(Item.images))
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found!")

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
        user_id=str(user_id),
        title="Item deleted successfully",
        message="Item deleted successfully",
        type=NotificationType.Item_Deleted,
    )

    return {"message": f"Item {item_id} deleted successfully!"}
