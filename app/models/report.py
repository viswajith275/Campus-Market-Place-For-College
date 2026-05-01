from datetime import datetime
from typing import Optional

from sqlalchemy import Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enum import ReportCategory


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[ReportCategory] = mapped_column(Enum(ReportCategory))
    description: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    reporter: Mapped["User"] = relationship("User", back_populates="reports")
    item: Mapped["Item"] = relationship("Item", back_populates="reports")
