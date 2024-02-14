import re
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
from datetime import date
from typing import List

from starlette import status

from src.constants.utilities import EMAIL_REGEX, PHONE_REGEX
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler

ARRIVAL_TIME = ["12.30-2.30", "2.30-5.00", "5.00-7.00", "7.00-9.00", "10.00-12.00"]


class Status(str, Enum):
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"
    checkedin = "CHECKED_IN"
    noshow = "NOSHOW"


class BookingUserStatus(str, Enum):
    confirmed = "CONFIRMED"
    cancelled = "CANCELLED"
    all = "ALL"


class GuestDetails(BaseModel):
    first_name: str = Field(default=None)
    last_name: str = Field(default=None)
    email: str = Field(default=None)
    phone_number: str = Field(default=None)


class Gender(str, Enum):
    male = "MALE"
    female = "FEMALE"
    other = "OTHER"


class GuestRegistrationDetails(BaseModel):
    first_name: str = Field(default=None)
    last_name: str = Field(default=None)
    email: str = Field(default=None)
    phone_number: str = Field(default=None)
    gender:Gender

    @validator("first_name")
    @classmethod
    def return_lower(cls, value):
        return value.lower()

    @validator("last_name")
    @classmethod
    def return_name_lower(cls, value):
        return value.lower()

    @validator("email")
    @classmethod
    def check_email(cls, value):
        pattern = re.compile(EMAIL_REGEX)
        if not pattern.match(value):
            raise CustomExceptionHandler(message="Please enter a valid email",
                                         code=status.HTTP_400_BAD_REQUEST,
                                         target="",
                                         success=False
                                         )
        return value

    @validator("phone_number")
    @classmethod
    def check_phone_number_regex(cls, value):
        pattern = re.compile(PHONE_REGEX)
        if not pattern.match(value):
            raise CustomExceptionHandler(message="Please enter a valid phone number",
                                         code=status.HTTP_400_BAD_REQUEST,
                                         target="",
                                         success=False
                                         )
        return value


class BookingGuest(BaseModel):
    booking_parent_id: int = Field(default=None)
    room_id: List[int] = Field(..., description="Room id")
    booking_date: date = Field(...)
    booking_time: datetime = Field(...)
    departure_date: date = Field(...)
    departure_time: datetime = Field(...)
    adults: int = Field(...)
    children: int = Field(...)
    rooms: int = Field(...)
    special_requirement: str = Field(...)
    booking_base_price: float = Field(...)
    is_booked_for_someone_else: bool = Field(default=False)
    guest_details: GuestRegistrationDetails
    status: Status = Field(...)
    created_at: datetime
    updated_at: datetime
    exceed_max_occupancy_limit: bool = Field(default=False)



class Booking(BaseModel):
    booking_parent_id: int = Field(default=None)
    room_id: List[int] = Field(..., description="Room id")
    booking_date: date = Field(...)
    booking_time: datetime = Field(...)
    departure_date: date = Field(...)
    departure_time: datetime = Field(...)
    adults: int = Field(...)
    children: int = Field(...)
    rooms: int = Field(...)
    special_requirement: str = Field(...)
    booking_base_price: float = Field(...)
    is_booked_for_someone_else: bool = Field(default=False)
    guest_details: GuestDetails
    status: Status = Field(...)
    created_at: datetime
    updated_at: datetime
    exceed_max_occupancy_limit: bool = Field(default=False)


class UpdateBooking(BaseModel):
    booking_parent_id: str = Field(..., description="Booking parent id")
    status = "CANCELLED"


class BookingType(BaseModel):
    booking_type: BookingUserStatus
