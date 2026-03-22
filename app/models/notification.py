from datetime import datetime
from typing import Dict

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import ForeignKey
from sqlalchemy.types import Enum

from app.db.base_class import Base
from app.models.enum import NotificationType


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[NotificationType] = mapped_column(Enum(NotificationType))
    title: Mapped[str] = mapped_column()
    message: Mapped[str] = mapped_column()
    is_read: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    payload: Mapped[Dict] = mapped_column(JSON, default="{}")

    user: Mapped["User"] = relationship("User", back_populates="notifications")
