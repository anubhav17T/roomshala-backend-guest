from datetime import datetime, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from src.constants.utilities import JWT_EXPIRATION_TIME, JWT_SECRET_KEY, JWT_ALGORITHM
import jwt

from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from src.utils.helpers.db_helpers import find_black_list_token, find_exist_guest

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/guest/login"
)



async def create_access_token(data: dict, expire_delta: timedelta = None):
    to_encode = data.copy()
    if expire_delta:
        expire = datetime.utcnow() + expire_delta
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_TIME)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    # username: str = payload.get("sub")
    username = payload["email"]
    if username is None:
        raise CustomExceptionHandler(message="Could Not Validate Credentials",
                                     success=False,
                                     code=status.HTTP_401_UNAUTHORIZED,
                                     target="GET_CURRENT_USER"
                                     )

    try:
        # Check blacklist token
        black_list_token = await find_black_list_token(token)
        if black_list_token:
            print("error in creds")
            raise CustomExceptionHandler(message="Could Not Validate Credentials",
                                         success=False,
                                         code=status.HTTP_401_UNAUTHORIZED,
                                         target="GET_CURRENT_USER"
                                         )
        # Check if user exist or not
        result = await find_exist_guest(email=username)
        if not result:
            raise CustomExceptionHandler(message="You are not registered yet,please register yourself",
                                         code=status.HTTP_404_NOT_FOUND,
                                         success=False,
                                         target="JWT-VERIFICATION"
                                         )
        return {"id": result["id"],
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "gender": result["gender"],
                "email": result["email"],
                "phone_number": result["phone_number"],
                "is_active": result["is_active"],
                "profile_url":result["profile_url"],
                "created_on": result["created_on"],
                "updated_on": result["updated_on"]
                }

    except Exception as e:
        raise CustomExceptionHandler(message="Something went wrong,please try again later",
                                     code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     success=False,
                                     target="JWT-VERIFICATION CAUSED[{}]".format(e)
                                     )

