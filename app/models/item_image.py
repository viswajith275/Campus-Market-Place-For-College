from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.models.enum import ImageStatus


class ItemImage(Base):
    __tablename__ = "item_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    image_path: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    status: Mapped[ImageStatus] = mapped_column(default=ImageStatus.Pending)
    # relationship with

    item: Mapped["Item"] = relationship("Item", back_populates="images")


@event.listens_for(ItemImage, "after_delete")
def delete_image_after_cascade(mapper, connection, image):

    if image.image_path:
        from app.tasks.images import delete_image_task

        delete_image_task.delay(image.image_path)
