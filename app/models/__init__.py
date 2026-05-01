from sqlalchemy import func, select
from sqlalchemy.orm import column_property

from app.db.base_class import Base
from app.models.bid import Bid
from app.models.item import Item
from app.models.item_image import ItemImage
from app.models.notification import Notification
from app.models.rating import Rating
from app.models.report import Report
from app.models.token import UserToken
from app.models.transaction import Transaction
from app.models.user import User

Item.bid_count = column_property(
    select(func.count(Bid.id))
    .where(Bid.item_id == Item.id)
    .correlate_except(Bid)
    .scalar_subquery()
)
