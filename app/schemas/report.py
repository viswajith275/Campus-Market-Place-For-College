from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enum import ReportCategory
from app.schemas.item import ItemResponse


class ReportResponse(BaseModel):
    category: ReportCategory
    description: Optional[str] = None
    item: ItemResponse

    model_config = ConfigDict(from_attributes=True)


class ReportCreate(BaseModel):
    category: ReportCategory
    description: Optional[str] = None
