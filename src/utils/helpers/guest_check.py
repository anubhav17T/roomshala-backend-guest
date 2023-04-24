from starlette import status
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from src.utils.helpers.db_helpers import guest_id, guest_email, guest_phone_number


class CheckGuest:
    def __init__(self, target: str, phone_number=None, email=None, id=None):
        self.phone_number = phone_number
        self.email = email
        self.target = target
        self.id = id

    async def find_guest_by_id(self):
        response = await guest_id(id=self.id)
        if response is  None:
            raise CustomExceptionHandler(message="You are already registered",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target=self.target
                                         )
        return response

    async def find_guest_by_phone_number(self):
        response = await guest_phone_number(phone_number=self.phone_number)
        if response is not None:
            raise CustomExceptionHandler(message="This number is already registered",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target=self.target
                                         )
        return response

    async def find_guest_by_email(self):
        response = await guest_email(email=self.email)
        if response is not None:
            raise CustomExceptionHandler(message="Email is already registered",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target=self.target
                                         )
        return response
