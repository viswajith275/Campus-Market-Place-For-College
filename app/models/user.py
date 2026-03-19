from datetime import datetime
from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    phone_no: Mapped[str] = mapped_column()
    hashed_password: Mapped[str] = mapped_column()
    disabled: Mapped[bool] = mapped_column(default=False)
    transaction_count: Mapped[int] = mapped_column(default=0)
    total_rating: Mapped[float] = mapped_column(default=0)
    rating: Mapped[float] = mapped_column(default=2.5)
    locked: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    tokens: Mapped[List["UserToken"]] = relationship(
        "UserToken", back_populates="user", cascade="all, delete-orphan"
    )

    listed_items: Mapped[List["Item"]] = relationship(
        "Item", back_populates="seller", cascade="all, delete-orphan"
    )
    all_bids: Mapped[List["Bid"]] = relationship(
        "Bid", back_populates="bider", cascade="all, delete-orphan"
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )
