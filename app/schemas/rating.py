from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.schemas.user import PublicUsersResponse


class RatingResponse(BaseModel):
    id: int
    rated_user: PublicUsersResponse
    score: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
