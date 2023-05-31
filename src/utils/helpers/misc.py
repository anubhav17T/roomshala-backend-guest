import json
import string
import re
from random import choice
from passlib.context import CryptContext
from pytz import timezone

from src.constants.utilities import BCRYPT_SCHEMA
from datetime import timedelta, datetime, date

from src.utils.helpers.db_helpers_property import find_particular_property_information, check_if_room_exist, \
    find_rooms_wise_price

pwd_context = CryptContext(schemes=[BCRYPT_SCHEMA])


def random(digits: int):
    chars = string.digits
    return "".join(choice(chars) for _ in range(digits))


def modify_docs(docs):
    return json.dumps(docs)


def check_password_strength(password):
    password_pattern = "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
    match = re.match(password_pattern, password)
    if match is None:
        return False
    return True


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_passwrd: str):
    return pwd_context.verify(plain_password, hashed_passwrd)


def user_price_distribution(base_booking_amount):
    if base_booking_amount < 2500:
        gst = 12
    else:
        gst = 18
    return {"booking_base_price": base_booking_amount,
            "gst_percentage": gst,
            "gst_amount": (base_booking_amount * gst) // 100,
            "booking_final_amount": base_booking_amount + (base_booking_amount * gst) // 100
            }


async def price_distribution_calculator(property_id, check_in_date, check_out_date, rooms, guests):
    dt = datetime.now(timezone("Asia/Kolkata"))
    property_information = await find_particular_property_information(id=property_id)
    if property_information is None:
        raise Exception("No property found")
    check_for_room = await check_if_room_exist(property_id=property_id)
    if check_for_room is None:
        raise Exception("No room exist")
    if check_in_date < dt.date():
        raise Exception("Check dates")
    if check_out_date < check_in_date:
        raise Exception("Check dates")
    delta = check_out_date - check_in_date
    delta_days = delta.days
    number_of_extra_guest = guests - 2 * rooms
    if number_of_extra_guest <=0:
        number_of_extra_guest = 0

    room_wise_price = await find_rooms_wise_price(property_id=property_id)
    pricing = []
    for i in room_wise_price:
        check = dict(i)
        price = user_price_distribution(check["base_room_price"])
        requested_metadata = {"number_of_nights": delta_days,
                              "number_of_extra_guests": number_of_extra_guest,
                              "extra_mattress_price": check["extra_mattress_price"],
                              "billed_extra_mattress_amount": check[
                                                                  "extra_mattress_price"] * number_of_extra_guest * delta_days,
                              "billed_base_amount": (check["base_room_price"] * delta_days * rooms) + (
                                      check["extra_mattress_price"] * number_of_extra_guest * delta_days),
                              "billed_gst_amount": "",
                              "billed_total_amount": ""
                              }
        if requested_metadata["billed_base_amount"] < 2500:
            gst = 12
        else:
            gst = 18
        requested_metadata.update({"billed_gst_amount": (requested_metadata["billed_base_amount"] * gst) // 100})
        requested_metadata.update({"billed_total_amount": (
                    requested_metadata["billed_base_amount"] + (requested_metadata["billed_gst_amount"]))})
        price.update({"requested_metadata": requested_metadata})
        price.pop("booking_base_price")
        # update price as per the requested details

        check.update(price)
        pricing.append(check)
    return pricing
