from datetime import datetime
from typing import Dict

from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.models.enum import NotificationType


class NotificationResponse(BaseModel):
    id: int
    type: NotificationType
    title: str
    message: str
    is_read: bool
    payload: Dict
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
