from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.models.enum import TransactionStatus
from app.schemas.item import ItemResponse
from app.schemas.user import ProtectedUserResponse


class SellerTransactionResponse(BaseModel):
    buyer: ProtectedUserResponse
    price: float
    status: TransactionStatus
    quantity: int
    item: ItemResponse

    model_config = ConfigDict(from_attributes=True)


class BuyerTransactionResponse(BaseModel):
    seller: ProtectedUserResponse
    price: float
    status: TransactionStatus
    quantity: int
    item: ItemResponse

    model_config = ConfigDict(from_attributes=True)
