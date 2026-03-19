from datetime import datetime
from typing import List, Optional

from sqlalchemy import Enum, ForeignKey, Index, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import TSVECTOR as PG_TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enum import ItemCategories, ItemCondition, ItemStatus


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    min_price: Mapped[float] = mapped_column()
    quantity: Mapped[int] = mapped_column()
    condition: Mapped[ItemCondition] = mapped_column()
    categories: Mapped[List[ItemCategories]] = mapped_column(
        ARRAY(Enum(ItemCategories)), server_default="{}"
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())

    status: Mapped[ItemStatus] = mapped_column(
        Enum(ItemStatus), default=ItemStatus.Active
    )

    search_vector: Mapped[Optional[str]] = mapped_column(PG_TSVECTOR, nullable=True)

    images: Mapped[List["ItemImage"]] = relationship(
        "ItemImage",
        back_populates="item",
        passive_deletes=True,
    )
    seller: Mapped["User"] = relationship("User", back_populates="listed_items")
    bids: Mapped[List["Bid"]] = relationship(
        "Bid", back_populates="item", cascade="all, delete-orphan"
    )
    transaction: Mapped["Transaction"] = relationship(
        back_populates="item", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_products_categories", "categories", postgresql_using="gin"),
        Index("ix_products_search_vector", "search_vector", postgresql_using="gin"),
        Index(
            "ix_products_categories_nonempty",
            "categories",
            postgresql_using="gin",
            postgresql_where=text("categories != '{}'"),
        ),
    )
