from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.enum import ReportCategory
from app.schemas.user import ProtectedUserResponse


class ReportResponse(BaseModel):
    category: ReportCategory
    description: Optional[str] = None
    reporter: ProtectedUserResponse

    model_config = ConfigDict(from_attributes=True)


class ReportCreate(BaseModel):
    category: ReportCategory
    description: Optional[str] = None
