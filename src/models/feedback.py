from enum import Enum

from pydantic import BaseModel, Field


class Feedback(BaseModel):
    booking_id: int = Field(..., description="Property ID")
    rating: int = Field(..., ge=0, le=5)
    comment: str = Field(..., description="")


class IssueType(str, Enum):
    payment_related = "PAYMENT"
    reservation_related = "RESERVATIONS"
    unavailable_rooms = "AVAILABILITY_ROOMS"
    technical_issue = "TECHNICAL_ISSUE"
    refund_request = "REFUND_REQUEST"
    promotions_discount = "PROMOTIONS"
    feedback = "FEEDBACK"
    other = "OTHER"


class Status(str, Enum):
    open = "OPEN"


class Ticket(BaseModel):
    issue_type: IssueType
    status: Status
    comment:str = Field(...,description="")