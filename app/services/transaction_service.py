from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.exceptions import BadRequest, NotFound
from app.models.bid import Bid
from app.models.enum import BidStatus, ItemStatus
from app.models.item import Item
from app.models.rating import Rating
from app.models.transaction import Transaction
from app.models.user import User


async def fetch_my_selled_transactions(
    user_id: int, db: AsyncSession
) -> Sequence[Transaction]:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.seller_id == user_id)
        .options(joinedload(Transaction.buyer), joinedload(Transaction.item))
    )

    transactions = result.scalars().all()

    if not transactions:
        raise NotFound("transactions not found!")

    return transactions


async def fetch_my_buyed_transactions(
    user_id: int, db: AsyncSession
) -> Sequence[Transaction]:
    result = await db.execute(
        select(Transaction)
        .where(Transaction.buyer_id == user_id)
        .options(joinedload(Transaction.seller), joinedload(Transaction.item))
    )

    transactions = result.scalars().all()

    if not transactions:
        raise NotFound("transactions not found!")

    return transactions


async def create_transaction(
    item_id: int, bid_id: int, user_id: int, db: AsyncSession
) -> Transaction:
    result = await db.execute(
        select(Item)
        .where(Item.id == item_id, Item.seller_id == user_id)
        .options(selectinload(Item.bids))
    )
    item = result.scalar_one_or_none()

    if item is None:
        raise NotFound("Item not Found!")

    result = await db.execute(
        select(Bid).where(Bid.id == bid_id, Bid.item_id == item_id)
    )
    bid = result.scalar_one_or_none()

    if bid is None:
        raise NotFound("Bid not found!")

    try:
        if bid.quantity > item.quantity:
            raise BadRequest("Item stock exceeded!")

        if bid.quantity == item.quantity:
            item.status = ItemStatus.Sold

            for b in item.bids:
                b.status = BidStatus.Rejected

        item.quantity -= bid.quantity

        bid.status = BidStatus.Accepted

        new_transaction = Transaction(
            item_id=item_id,
            bid_id=bid_id,
            seller_id=user_id,
            buyer_id=bid.bider_id,
            price=bid.price,
            quantity=bid.quantity,
        )

        db.add(new_transaction)

        await db.flush()
        await db.refresh(new_transaction)

        # Todo make rating entries and update user locked status

        seller_rating = Rating(
            rater_id=user_id, rated_id=bid.bider_id, transaction_id=new_transaction.id
        )
        bider_rating = Rating(
            rater_id=bid.bider_id, rated_id=user_id, transaction_id=new_transaction.id
        )

        ratings = [seller_rating, bider_rating]

        db.add_all(ratings)

        result = await db.execute(select(User).where(User.id == user_id))
        seller = result.scalar_one_or_none()

        if seller is None:
            raise NotFound("User does not exist!")

        result = await db.execute(select(User).where(User.id == bid.bider_id))
        bider = result.scalar_one_or_none()

        if bider is None:
            raise NotFound("User does not exist!")

        seller.transaction_count += 1
        seller.locked = True
        bider.transaction_count += 1
        bider.locked = True

        await db.commit()

    except Exception as e:
        await db.rollback()

        raise e

    return new_transaction
