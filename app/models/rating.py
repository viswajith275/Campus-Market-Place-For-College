from datetime import datetime
from typing import Optional

# import uuid    use as a secondary level of primary for security
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enum import RatingStatus


class Rating(Base):
    __tablename__ = "ratings"

    id: Mapped[int] = mapped_column(primary_key=True)

    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    rater_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rated_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    score: Mapped[Optional[float]] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    status: Mapped[RatingStatus] = mapped_column(default=RatingStatus.Pending)

    # relationship with

    transaction: Mapped["Transaction"] = relationship(back_populates="ratings")
    rater_user: Mapped["User"] = relationship(foreign_keys=[rater_id])
    rated_user: Mapped["User"] = relationship(foreign_keys=[rated_id])
