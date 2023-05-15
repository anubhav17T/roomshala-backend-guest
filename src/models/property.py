import re

from enum import Enum
from fastapi import Query
from pydantic import BaseModel, Field, validator
from src.constants.utilities import EMAIL_REGEX, PHONE_REGEX
from starlette import status

from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler


class MarkPropertyFavourite(BaseModel):
    property_id: int = Field()


class UpdateMarkPropertyFavourite(BaseModel):
    property_id: int = Field(..., description="Hotel id")
    is_active:bool = Field(default=False,description="")