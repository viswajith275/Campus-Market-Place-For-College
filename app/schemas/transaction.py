from pydantic import BaseModel
from pydantic.config import ConfigDict

from app.models.enum import TransactionStatus
from app.schemas.item import BuyerTransactionItemResponse, SellerTransactionItemResponse
from app.schemas.user import ProtectedUserResponse


class SellerTransactionResponse(BaseModel):
    buyer: ProtectedUserResponse
    price: float
    status: TransactionStatus
    quantity: int
    item: SellerTransactionItemResponse

    model_config = ConfigDict(from_attributes=True)


class BuyerTransactionResponse(BaseModel):
    price: float
    status: TransactionStatus
    quantity: int
    item: BuyerTransactionItemResponse

    model_config = ConfigDict(from_attributes=True)
