from datetime import timedelta, datetime

from fastapi import APIRouter, Query, Path, Depends
from starlette import status
from src.models.booking import Booking, UpdateBooking, BookingType
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from src.utils.helpers.asset_check import AssetValidation, TimeslotConfiguration
from src.utils.helpers.db_helpers import create_booking, find_booking, find_booking_for_guest, update_booking, \
    find_upcoming_booking, find_previous_booking
from src.utils.helpers.jwt_utils import get_current_user
from src.utils.helpers.misc import user_price_distribution
from src.utils.logger.logger import logger
from src.utils.response.data_response import ResponseModel
from pytz import timezone

booking_engine = APIRouter()

DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]


@booking_engine.post("/property/booking")
async def booking(book: Booking, current_user=Depends(get_current_user)):
    logger.info("CREATING BOOKING FOR {}".format(current_user["first_name"]))
    logger.info("VALIDATING CHECKS FOR ROOM AND HOTEL")
    asset = AssetValidation(room_id=book.room_id)
    check = await asset.validate_property_info()
    # time based checks
    try:
        time_based = TimeslotConfiguration(booking_date=book.booking_date,
                                           departure_date=book.departure_date,
                                           booking_time=book.booking_time,
                                           departure_time=book.departure_time
                                           )
        await time_based.compare_date()
        await time_based.validate_booking_time()
        await time_based.validate_departure_time()
        await time_based.validate_departure_date()
        await time_based.check_if_start_date_valid()
        await time_based.check_if_booking_time_less_current_time()
    except Exception as why:
        logger.error("######### ERROR IN TIMESLOT CONFIGURATION CHECKS BECAUSE {} ##############".format(why))
        raise CustomExceptionHandler(
            message="Something went wrong on our end,please try again later.",
            success=False,
            code=status.HTTP_409_CONFLICT,
            target="CREATE BOOKING CANNOT ABLE TO CREATE BOOKING BECAUSE {}".format(why)
        )
    if book.children > 2:
        raise CustomExceptionHandler(
            message="Sorry, Cannot allow more than 2 children.",
            success=False,
            code=status.HTTP_409_CONFLICT,
            target="CREATE_BOOKING")

    if not book.exceed_max_occupancy_limit:
        await asset.validate_room_max_occupancy(adults=book.adults)

    # check if room has that day availability
    room_info = await asset.find_room_info()
    room_available_days = room_info["days"]
    user_requesting_for_book_days = []
    start_date = book.booking_date
    end_date = book.departure_date
    d = end_date - start_date
    for i in range(d.days + 1):
        day = start_date + timedelta(days=i)
        user_requesting_for_book_days.append(day.strftime("%A").upper())
    for i in user_requesting_for_book_days:
        if i not in room_available_days:
            raise CustomExceptionHandler(
                message="This is on us,Please try again after sometime",
                success=False,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                target="ROOM_NOT_AVAILABLE_FOR_PARTICULAR_DAY "
                       "AVAILABLE_DAYS = {}"
                       "REQUEST_DAYS = {}".format(room_available_days, user_requesting_for_book_days)
            )
    if book.booking_base_price != room_info["base_room_price"]:
        raise CustomExceptionHandler(
            message="This is on us,Please try again after sometime",
            success=False,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            target="Please validate the price")

    # CHECK FOR MIDDLE DATE, CHECK IF ROOM_ID IS THERE AND CHECK IF THAT DATE IS MIDDLE
    await asset.check_for_overlapping_date(booking_time=book.booking_time,
                                           departure_time=book.departure_time,
                                           room_id=book.room_id
                                           )
    await asset.check_for_no_booking_date(booking_date=book.booking_date,
                                          departure_date=book.departure_date,
                                          user_id=current_user["id"]
                                          )
    await asset.check_for_no_booking(booking_time=book.booking_time,
                                     departure_time=book.departure_time
                                     )
    reservation_id = await create_booking(book=book, property=check,
                                          user_info=current_user
                                          )

    if reservation_id is None:
        raise CustomExceptionHandler(
            message="This is on us,Please try again after sometime",
            success=False,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            target="CREATE_RESERVATION"
        )
    return ResponseModel(message="Enjoy Your Stay. Happy to serve you",
                         success=True,
                         code=status.HTTP_200_OK,
                         data=await find_booking(id=reservation_id)
                         ).response()


@booking_engine.patch("/property/booking")
async def booking(update: UpdateBooking, current_user=Depends(get_current_user)):
    logger.info("CREATING BOOKING FOR {}".format(current_user["first_name"]))
    booking_info = await find_booking_for_guest(id=update.booking_id, user_id=current_user["id"])
    if booking_info is None:
        raise CustomExceptionHandler(
            message="No booking found!",
            success=False,
            code=status.HTTP_404_NOT_FOUND,
            target="UPDATE_RESERVATION"
        )
    if booking_info["status"] != "CONFIRMED":
        raise CustomExceptionHandler(
            message="Cannot Cancel This booking at this time",
            success=False,
            code=status.HTTP_404_NOT_FOUND,
            target="BOOKING_STATUS"
        )
    dt = datetime.now(timezone("Asia/Kolkata"))
    diff = booking_info["booking_time"] - dt.now()
    days, seconds = diff.days, diff.seconds
    hours = days * 24 + seconds // 3600
    if hours < 24:
        raise CustomExceptionHandler(
            message="Sorry,You can only cancel booking prior 24Hours",
            success=False,
            code=status.HTTP_409_CONFLICT,
            target="BOOKING_STATUS"
        )
    if dt.date() >= booking_info["booking_date"]:
        raise CustomExceptionHandler(
            message="Sorry,You can only cancel booking prior 24Hours",
            success=False,
            code=status.HTTP_409_CONFLICT,
            target="BOOKING_STATUS"
        )
    success = await update_booking(booking_id=update.booking_id,
                                   user=current_user
                                   )
    if success is None:
        raise CustomExceptionHandler(
            message="This is on our end,Please Try again later ",
            success=False,
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            target="BOOKING_UPDATE_ISSUE"
        )
    return ResponseModel(message="Updated Successfully!!",
                         success=True,
                         code=status.HTTP_200_OK,
                         data=await find_booking_for_guest(user_id=current_user["id"], id=update.booking_id)
                         ).response()


@booking_engine.get("/property/upcoming/booking/{booking_status}")
async def booking(booking_status: str, current_user=Depends(get_current_user)):
    if booking_status is not None:
        if booking_status not in ["CONFIRMED", "CANCELLED", "ALL"]:
            raise CustomExceptionHandler(
                message="Please check status",
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                target="ENUM_STATUS"
            )
    dt = datetime.now(timezone("Asia/Kolkata"))
    upcoming_booking = await find_upcoming_booking(status=booking_status, time=dt.now(), user_id=current_user["id"])
    return ResponseModel(message="Please Find your bookings",
                         success=True,
                         code=status.HTTP_200_OK,
                         data=upcoming_booking
                         ).response()


@booking_engine.get("/property/past/booking/{booking_status}")
async def booking(booking_status: str, current_user=Depends(get_current_user)):
    if booking_status is not None:
        if booking_status not in ["CHECKED_IN", "CANCELLED", "CONFIRMED", "NOSHOW"]:
            raise CustomExceptionHandler(
                message="Please check status",
                success=False,
                code=status.HTTP_400_BAD_REQUEST,
                target="ENUM_STATUS"
            )
    dt = datetime.now(timezone("Asia/Kolkata"))
    previous_booking = await find_previous_booking(status=booking_status, time=dt.now(), user_id=current_user["id"])
    return ResponseModel(message="Please Find your bookings",
                         success=True,
                         code=status.HTTP_200_OK,
                         data=previous_booking
                         ).response()


@booking_engine.get("/property/base-amount/{base}/user")
async def booking(base: float = Query(...)):
    return user_price_distribution(base_booking_amount=base)
