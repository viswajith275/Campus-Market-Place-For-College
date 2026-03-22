from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    bid,
    item,
    item_image,
    notification,
    rating,
    transaction,
)

router = APIRouter()

router.include_router(auth.router, tags=["Auth"])
router.include_router(item.router, tags=["Item"], prefix="/items")
router.include_router(item_image.router, tags=["Image"], prefix="/images")
router.include_router(bid.router, tags=["Bid"], prefix="/bids")
router.include_router(transaction.router, tags=["Transaction"], prefix="/transactions")
router.include_router(rating.router, tags=["Rating"], prefix="/ratings")
router.include_router(
    notification.router, tags=["Notification"], prefix="/notifications"
)
