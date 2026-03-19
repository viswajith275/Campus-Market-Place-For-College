from datetime import datetime

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enum import BidStatus


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
    bider_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    price: Mapped[float] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    status: Mapped[BidStatus] = mapped_column(
        Enum(BidStatus), default=BidStatus.Pending
    )

    item: Mapped["Item"] = relationship(back_populates="bids")
    bider: Mapped["User"] = relationship(back_populates="all_bids")
