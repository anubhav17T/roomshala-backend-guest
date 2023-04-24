from enum import Enum
from pydantic import BaseModel, Field, validator
from starlette import status
from src.constants.utilities import PHONE_REGEX
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
import re


class OTPType(str, Enum):
    phone = "phone_number"


class CreateOtp(BaseModel):
    recipient_id: str = Field(..., description="Guest Mobile Number")

    @validator("recipient_id")
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




# class VerifyOTP(CreateOTP):
#     session_id: str
#     otp_code: str
#
#
# class OTPList(VerifyOTP):
#     otp_failed_count = int
#     status: str
