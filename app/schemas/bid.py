from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.enum import BidStatus
from app.schemas.user import PublicUsersResponse


class BidResponse(BaseModel):
    id: int
    price: float
    quantity: int
    bider: PublicUsersResponse
    status: BidStatus

    model_config = ConfigDict(from_attributes=True)


class BidCreate(BaseModel):
    price: float
    quantity: int

    @field_validator("price")
    @classmethod
    def bid_price_validator(cls, p: float | None) -> float | None:
        if p is not None and p < 0:
            raise ValueError("The price cannot be less than 0!")
        return p

    @field_validator("quantity")
    @classmethod
    def quantity_validator(cls, q: int | None) -> int | None:
        if q is not None and q < 0:
            raise ValueError("Quantity should be greater than 0!!")
        return q


class BidUpdate(BidCreate):
    price: Optional[float] = None
    quantity: Optional[int] = None
