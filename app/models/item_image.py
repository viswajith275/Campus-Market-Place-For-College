from datetime import datetime

from sqlalchemy import ForeignKey, event
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base
from app.tasks.images import delete_image_task


class ItemImage(Base):
    __tablename__ = "item_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))

    image_path: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    # relationship with

    item: Mapped["Item"] = relationship("Item", back_populates="images")


@event.listens_for(ItemImage, "after_delete")
def delete_image_after_cascade(mapper, connection, image):

    if image.image_path:
        delete_image_task.delay(image.image_path)
