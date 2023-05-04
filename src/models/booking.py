from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from datetime import date

ARRIVAL_TIME = ["12.30-2.30", "2.30-5.00", "5.00-7.00", "7.00-9.00", "10.00-12.00"]


class Status(str, Enum):
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"
    checkedin = "CHECKED_IN"
    noshow = "NOSHOW"

class BookingUserStatus(str,Enum):
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"
    all = "ALL"



class Booking(BaseModel):
    room_id: int = Field(..., description="Room id")
    booking_date: date = Field(...)
    booking_time: datetime = Field(...)
    departure_date: date = Field(...)
    departure_time: datetime = Field(...)
    adults: int = Field(...)
    children: int = Field(...)
    special_requirement: str = Field(...)
    booking_base_price: float = Field(..., gt=200)
    gst_percentage: float = Field(...)
    gst_amount: float = Field(...)
    booking_final_amount: float = Field(...)
    status: Status = Field(...)
    created_at: datetime
    updated_at: datetime
    exceed_max_occupancy_limit: bool = Field(default=False)


class UpdateBooking(BaseModel):
    booking_id: int = Field(..., description="Booking id")
    status = "CANCELLED"


class BookingType(BaseModel):
    booking_type: BookingUserStatus
