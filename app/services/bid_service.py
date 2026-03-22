from typing import Dict

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import BadRequest, Conflict, NotFound
from app.models.bid import Bid
from app.models.enum import BidStatus, NotificationType
from app.models.item import Item
from app.schemas.bid import BidCreate, BidUpdate
from app.services.notification_service import notify


async def create_bid(
    item_id: int, user_id: int, bid_request: BidCreate, db: AsyncSession
) -> Bid:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not found!")

    if item.seller_id == user_id:
        raise Conflict("You cannot bid on your item!")

    if bid_request.quantity > item.quantity:
        raise BadRequest("The item stock has exceeded!")

    if bid_request.price < item.min_price:
        raise BadRequest("Bid price too low!")

    result = await db.execute(
        select(exists().where(Bid.item_id == item_id, Bid.bider_id == user_id))
    )

    existing_bid = result.scalar()

    if existing_bid:
        raise Conflict("You already have a bid on this item!")

    new_bid = Bid(
        price=bid_request.price,
        quantity=bid_request.quantity,
        item_id=item.id,
        bider_id=user_id,
    )

    db.add(new_bid)

    await db.commit()
    await db.refresh(new_bid)

    notify(
        user_id=str(user_id),
        title="Bid created successfully",
        message=f"Bid of {new_bid.price} has been successfully created for {item.title}",
        type=NotificationType.Bid_Created,
    )

    return new_bid


async def update_bid(
    bid_id: int, user_id: int, bid_patch: BidUpdate, db: AsyncSession
) -> Bid:
    result = await db.execute(
        select(Bid)
        .where(
            Bid.id == bid_id, Bid.bider_id == user_id, Bid.status == BidStatus.Pending
        )
        .options(selectinload(Bid.item))
    )

    bid = result.scalar_one_or_none()

    if bid is None:
        raise NotFound("Bid not found!")

    if bid_patch.quantity is not None and bid.quantity > bid.item.quantity:
        raise BadRequest("The item stock has exceeded!")

    if bid_patch.price is not None and bid_patch.price < bid.item.min_price:
        raise BadRequest("Bid price too low!")

    patch_data = bid_patch.model_dump(exclude_unset=True)

    if not patch_data:
        raise BadRequest("Nothing to update!")

    for key, value in patch_data.items():
        setattr(bid, key, value)

    await db.commit()
    notify(
        user_id=str(user_id),
        title="Bid updated successfully",
        message="Bid Successfully updated!",
        type=NotificationType.Bid_Updated,
    )

    return bid


async def delete_bid(bid_id: int, user_id: int, db: AsyncSession) -> Dict:
    result = await db.execute(
        select(Bid)
        .where(
            Bid.id == bid_id, Bid.bider_id == user_id, Bid.status == BidStatus.Pending
        )
        .options(selectinload(Bid.item))
    )

    bid = result.scalar_one_or_none()

    if bid is None:
        raise NotFound("Bid not found!")

    await db.delete(bid)
    await db.commit()

    notify(
        user_id=str(user_id),
        title="Bid deleted successfully",
        message="Bid Successfully deleted!",
        type=NotificationType.Bid_Deleted,
    )

    return {"message": "Bid deleted successfully!"}
