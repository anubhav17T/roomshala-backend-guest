from datetime import datetime, timedelta, date
from src.utils.helpers.db_helpers_property import find_particular_room_information, \
    find_particular_property_information, find_room_booking, find_room_booking_date, find_middle_booking
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from starlette import status
from pytz import timezone


class AssetValidation:
    def __init__(self, room_id):
        self.room_id = room_id

    async def find_room_info(self):
        return await find_particular_room_information(id=self.room_id)

    async def validate_property_info(self):
        check = await find_particular_room_information(id=self.room_id)
        if check is None:
            raise CustomExceptionHandler(message="This is on our end.Please check again later",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="VALIDATE_PROPERTY_NO_ROOM_FOUND"
                                         )
        property = await find_particular_property_information(id=check["property_id"])
        if property is None:
            raise CustomExceptionHandler(message="This is on our end.Please check again later",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="PROPERTY_IS_NOT_ACTIVE"
                                         )
        return property

    async def validate_room_max_occupancy(self, adults):
        check = await find_particular_room_information(id=self.room_id)
        if check["max_occupancy"] < adults:
            raise CustomExceptionHandler(message="This is on our end.Please check again later",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="MAX_OCCUPANCY_IS_LESS"
                                         )
        return True

    async def check_for_no_booking_date(self, booking_date, departure_date, user_id):
        check = await find_room_booking_date(room_id=self.room_id,
                                             booking_date=booking_date,
                                             departure_date=departure_date,
                                             user_id=user_id
                                             )
        if check is not None:
            raise CustomExceptionHandler(message="You have already booked this room,for provided date",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="check_for_no_booking_date".upper()
                                         )
        return True

    async def check_for_no_booking(self, booking_time, departure_time):
        check = await find_room_booking(room_id=self.room_id,
                                        booking_time=booking_time,
                                        departure_time=departure_time
                                        )
        if check is not None:
            raise CustomExceptionHandler(message="Room not available",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="Room is occupied at that time"
                                         )
        return True

    @staticmethod
    async def check_for_overlapping_date(booking_time, departure_time, room_id):
        check = await find_middle_booking(booking_time=booking_time, departure_time=departure_time,
                                          room_id=room_id)
        if check is not None:
            raise CustomExceptionHandler(message="Room not available, Overlapping date",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="Room is occupied at that time"
                                         )
        return True


class TimeslotConfiguration:
    def __init__(self, booking_date: date, departure_date: date, booking_time: datetime,
                 departure_time: datetime
                 ):
        self.booking_date = booking_date
        self.departure_date = departure_date
        self.booking_time = booking_time
        self.departure_time = departure_time
        self.dt = datetime.now(timezone("Asia/Kolkata"))

    async def compare_date(self):
        if self.booking_date != self.booking_time.date():
            raise Exception("Booking date mismatch")
        if self.departure_date !=self.departure_time.date():
            raise Exception("Departure date mismatch")

    async def validate_departure_date(self):
        if self.departure_time < self.booking_time:
            raise Exception("Departure datetime is less than booking date")
        return True

    async def validate_booking_time(self):
        if self.booking_time.hour < 12:
            raise Exception("Booking Time should be after 12.00 P.M")

    async def validate_departure_time(self):
        if self.departure_time.hour > 11:
            raise Exception("Departure Should be before 11.00 A.M")

    async def check_if_start_date_valid(self):
        if self.booking_time.date() < self.dt.date():
            raise Exception("Date is not valid, please specify current or future date")
        return True

    async def check_if_booking_time_less_current_time(self):
        if self.booking_time < self.dt.now():
            raise Exception("Booking time cannot be less than present time")
        return True
