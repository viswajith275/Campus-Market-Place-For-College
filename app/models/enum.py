from enum import Enum


class ItemStatus(Enum):
    Active = "Active"
    Sold = "Sold"


class ItemCondition(Enum):
    New = "New"
    Lightly_Used = "Lightly_Used"
    Heavily_Used = "Heavily_Used"


class BidStatus(Enum):
    Accepted = "Accepted"
    Pending = "Pending"
    Rejected = "Rejected"


class TransactionStatus(Enum):
    Pending = "Pending"
    Completed = "Completed"


class RatingStatus(Enum):
    Pending = "Pending"
    Completed = "Completed"


class NotificationType(Enum):
    Bid_Accepted = "Bid_Accepted"
    Bid_Rejected = "Bid_Rejected"
    Transaction_Pending = "Transaction_Pending"
    Transaction_Completed = "Transaction_Completed"
    Rating_Pending = "Rating_Pending"
    Rating_Received = "Rating_Received"


class ItemCategories(Enum):
    Electronics = "Electronics"
    Stationary = "Stationary"
    Rent = "Rent"
    Misselaneous = "Misseleneous"
