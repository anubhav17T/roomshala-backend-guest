import re

from enum import Enum
from fastapi import Query
from pydantic import BaseModel, Field, validator
from src.constants.utilities import EMAIL_REGEX, PHONE_REGEX
from starlette import status

from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler


class Gender(str, Enum):
    male = "MALE"
    female = "FEMALE"
    other = "OTHER"


class Guest(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Query(..., regex=EMAIL_REGEX)
    password: str = Field(..., example="test@123")
    phone_number: str = Field(default=None)
    gender: Gender = Field(default=None)

    @validator("first_name")
    @classmethod
    def return_lower(cls, value):
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


class ForgotPassword(BaseModel):
    email: str = Field(..., description="Mail")

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


class ResetPassword(BaseModel):
    reset_password_token: str
    new_password: str
    confirm_password: str


class ChangePassword(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class UpdateGuest(BaseModel):
    first_name: str = None
    last_name: str = None
    gender: Gender = Field(default=None)
    phone_number: str = None
    is_active: bool = None

    @validator("first_name")
    @classmethod
    def return_lower(cls, value):
        return value.lower()

    @validator("last_name")
    @classmethod
    def return_lowe_last_name(cls, value):
        return value.lower()


