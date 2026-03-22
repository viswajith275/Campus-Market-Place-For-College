from enum import Enum


class ItemStatus(str, Enum):
    Active = "Active"
    Sold = "Sold"


class ItemCondition(str, Enum):
    New = "New"
    Lightly_Used = "Lightly_Used"
    Heavily_Used = "Heavily_Used"


class BidStatus(str, Enum):
    Accepted = "Accepted"
    Pending = "Pending"
    Rejected = "Rejected"


class TransactionStatus(str, Enum):
    Pending = "Pending"
    Completed = "Completed"


class RatingStatus(str, Enum):
    Pending = "Pending"
    Completed = "Completed"


class NotificationType(str, Enum):
    Item_Created = "Item_Created"
    Item_Updated = "Item_Updated"
    Item_Deleted = "Item_Deleted"
    Bid_Created = "Bid_Created"
    Bid_Updated = "Bid_Updated"
    Bid_Accepted = "Bid_Accepted"
    Bid_Rejected = "Bid_Rejected"
    Bid_Deleted = "Bid_Deleted"
    Rating_Pending = "Rating_Pending"
    Rating_Received = "Rating_Received"


class ItemCategories(Enum):
    Electronics = "Electronics"
    Stationary = "Stationary"
    Rent = "Rent"
    Misseleneous = "Misseleneous"
