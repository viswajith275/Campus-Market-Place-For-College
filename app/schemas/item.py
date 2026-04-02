from typing import List, Optional

from pydantic import BaseModel, field_validator
from pydantic.config import ConfigDict

from app.models.enum import BidStatus, ItemCategory, ItemCondition, ItemStatus
from app.schemas.bid import BidResponse
from app.schemas.item_image import ItemImageResponse
from app.schemas.report import ReportResponse
from app.schemas.user import ProtectedUserResponse, PublicUsersResponse


class ItemResponse(BaseModel):
    id: int
    seller: PublicUsersResponse
    title: str
    description: str
    min_price: float
    quantity: int
    bid_count: int
    status: ItemStatus
    categories: List[ItemCategory]
    condition: ItemCondition
    images: List[ItemImageResponse] = []

    model_config = ConfigDict(from_attributes=True)


class BidItemResponse(BaseModel):
    id: int
    title: str
    seller: PublicUsersResponse
    min_price: float
    categories: List[ItemCategory]
    condition: ItemCondition

    model_config = ConfigDict(from_attributes=True)


class BidHistoryResponse(BaseModel):
    id: int
    price: float
    quantity: int
    bider: PublicUsersResponse
    status: BidStatus
    item: BidItemResponse

    model_config = ConfigDict(from_attributes=True)


class BuyerTransactionItemResponse(BaseModel):
    id: int
    title: str
    seller: ProtectedUserResponse
    categories: List[ItemCategory]
    condition: ItemCondition

    model_config = ConfigDict(from_attributes=True)


class SellerTransactionItemResponse(BaseModel):
    id: int
    title: str
    categories: List[ItemCategory]
    condition: ItemCondition

    model_config = ConfigDict(from_attributes=True)


class UniqueItemResponse(ItemResponse):
    bids: List[BidResponse]

    model_config = ConfigDict(from_attributes=True)


class AdminItemResponse(ItemResponse):
    seller: ProtectedUserResponse


class AdminUniqueItemResponse(AdminItemResponse):
    reports: List[ReportResponse]

    model_config = ConfigDict(from_attributes=True)


class ItemCreate(BaseModel):
    title: str
    description: str
    min_price: float
    quantity: int
    condition: ItemCondition
    categories: List[ItemCategory]

    @field_validator("title")
    @classmethod
    def title_validator(cls, t: str | None) -> str | None:
        if t is not None:
            if len(t) < 1:
                ValueError("Title should not be empty!")
            if len(t) > 25:
                ValueError("Title should not be greater than 25 characters!")
        return t

    @field_validator("description")
    @classmethod
    def description_validator(cls, d: str | None) -> str | None:
        if d is not None:
            if len(d) < 1:
                ValueError("Description should not be empty!")
            if len(d) > 500:
                ValueError("Description should not be greater than 500 characters!")
        return d

    @field_validator("min_price")
    @classmethod
    def price_validator(cls, p: float | None) -> float | None:
        if p is not None and p < 0:
            ValueError("Price should be greater than 0!")
        return p

    @field_validator("quantity")
    @classmethod
    def quantity_validator(cls, q: int | None) -> int | None:
        if q is not None and q < 0:
            ValueError("Quantity should be greater than 0!")
        return q

    @field_validator("categories")
    @classmethod
    def category_validator(
        cls, c: List[ItemCategory] | None
    ) -> List[ItemCategory] | None:
        if c is not None and len(set(c)) != len(c):
            ValueError("Same category was assigned twice!")
        return c


class ItemUpdate(ItemCreate):
    title: Optional[str] = None
    description: Optional[str] = None
    min_price: Optional[float] = None
    quantity: Optional[int] = None
    condition: Optional[ItemCondition] = None
    categories: Optional[List[ItemCategory]] = None
