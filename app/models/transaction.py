from datetime import datetime
from typing import List

# import uuid    use as a secondary level of primary for security
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enum import TransactionStatus


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    bid_id: Mapped[int] = mapped_column(ForeignKey("bids.id"))
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    price: Mapped[float] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    status: Mapped[TransactionStatus] = mapped_column(default=TransactionStatus.Pending)

    item: Mapped["Item"] = relationship(back_populates="transaction")
    ratings: Mapped[List["Rating"]] = relationship(
        back_populates="transaction", cascade="all, delete-orphan"
    )
    seller: Mapped["User"] = relationship(foreign_keys=[seller_id])
    buyer: Mapped["User"] = relationship(foreign_keys=[buyer_id])
