from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.models.enum import RatingStatus
from app.schemas.user import PublicUsersResponse


class RatingResponse(BaseModel):
    id: int
    rated_user: PublicUsersResponse
    score: Optional[int] = None
    created_at: datetime
    status: RatingStatus

    model_config = ConfigDict(from_attributes=True)
