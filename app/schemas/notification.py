from datetime import datetime

from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.models.enum import NotificationType


class NotificationResponse(BaseModel):
    type: NotificationType
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
