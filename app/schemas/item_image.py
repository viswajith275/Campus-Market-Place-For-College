from typing import Optional

from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.models.enum import ImageStatus


class ItemImageResponse(BaseModel):
    id: int
    image_path: Optional[str] = None
    status: ImageStatus

    model_config = ConfigDict(from_attributes=True)
