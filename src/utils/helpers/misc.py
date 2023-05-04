import string
import re
from random import choice
from passlib.context import CryptContext

from src.constants.utilities import BCRYPT_SCHEMA

pwd_context = CryptContext(schemes=[BCRYPT_SCHEMA])


def random(digits: int):
    chars = string.digits
    return "".join(choice(chars) for _ in range(digits))


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
