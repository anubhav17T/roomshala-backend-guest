import re
import uuid
from typing import Optional
from fastapi import APIRouter, Query, Path, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi.encoders import jsonable_encoder

from src.constants.utilities import JWT_EXPIRATION_TIME
from src.models.property import MarkPropertyFavourite, UpdateMarkPropertyFavourite
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from src.models.guest import Guest, ForgotPassword, ResetPassword, UpdateGuest, ChangePassword
from src.utils.helpers import jwt_utils
from src.utils.helpers.db_helpers import add_guest, create_reset_code, check_reset_password_token, reset_admin_password, \
    disable_reset_code, guest_registered_with_mail_or_phone, guest_email, update_guest, get_protected_password, \
    guest_change_password, add_guest_fav_property, update_guest_fav_property, check_fav_property_existence, \
    find_user_fav_properties
from src.utils.helpers.db_helpers_property import find_particular_property_information
from src.utils.helpers.guest_check import CheckGuest
from src.utils.helpers.misc import check_password_strength, hash_password, verify_password
from src.utils.logger.logger import logger
from src.models.otp import CreateOtp
from src.utils.response.data_response import ResponseModel
from src.utils.helpers.jwt_utils import create_access_token, get_current_user
from datetime import datetime
from pytz import timezone

guest = APIRouter()


@guest.post("/otp/send")
async def send_otp(otp: CreateOtp):
    logger.info("CREATING OTP FOR RECIPIENT ID {}".format(otp.recipient_id))


@guest.get("/check/password-pattern/{password}")
async def check_password(password: str = Path(...)):
    match = check_password_strength(password=password)
    if not match:
        raise CustomExceptionHandler(message="Password pattern mismatch",
                                     target="Check_Regex_Password",
                                     code=status.HTTP_400_BAD_REQUEST,
                                     success=False
                                     )
    return ResponseModel(message="Password is a match",
                         code=status.HTTP_200_OK,
                         success=True,
                         data={}
                         )


@guest.get("/check-registration/{type}/{value}")
async def check_guest_registration(type: str = Path(...), value: str = Path(...)):
    if type not in ["EMAIL", "PHONE_NUMBER"]:
        raise CustomExceptionHandler(message="Please Check Available Type Values [EMAIL/PHONE_NUMBER]",
                                     target="Check_Guest_Mode_Type",
                                     code=status.HTTP_400_BAD_REQUEST,
                                     success=False
                                     )
    find_guest = CheckGuest(target="CHECK_GUEST",
                            phone_number=value,
                            email=value)
    if type == "EMAIL":
        await find_guest.find_guest_by_email()
    elif type == "PHONE_NUMBER":
        await find_guest.find_guest_by_phone_number()
    return ResponseModel(message="Guest doesn't exist",
                         success=True,
                         code=status.HTTP_200_OK,
                         data={}
                         )


@guest.post("/register")
async def register_guest(guest: Guest):
    guest_map = jsonable_encoder(guest)
    logger.info("CHECKING IF CLIENT EXIST OR NOT")
    find_guest = CheckGuest(target="CHECK_GUEST",
                            phone_number=guest_map["phone_number"],
                            email=guest_map["email"])

    await find_guest.find_guest_by_email()
    await find_guest.find_guest_by_phone_number()
    # check password strength
    match = check_password_strength(password=guest_map["password"])
    if not match:
        raise CustomExceptionHandler(message="Password pattern mismatch",
                                     target="Check_Regex_Password",
                                     code=status.HTTP_400_BAD_REQUEST,
                                     success=False
                                     )
    guest_map["password"] = hash_password(guest_map["password"])
    success = await add_guest(guest_map)
    if success is None:
        raise CustomExceptionHandler(message="Something went wrong,Please try again later",
                                     code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     target="CHECK_ADMIN",
                                     success=False
                                     )
    access_token_expires = jwt_utils.timedelta(minutes=JWT_EXPIRATION_TIME)
    access_token = await create_access_token(data=guest_map,
                                             expire_delta=access_token_expires
                                             )
    return ResponseModel(message="Welcome to roomshala,account created",
                         code=status.HTTP_201_CREATED,
                         success=True,
                         data={"access_token": access_token,
                               "token_type": "bearer",
                               "id": success,
                               "first_name": guest_map["first_name"],
                               "last_name": guest_map["last_name"],
                               "gender": guest_map["gender"],
                               "email": guest_map["email"],
                               "phone_number": guest_map["phone_number"],
                               "profile_url": guest_map["profile_url"]
                               }
                         ).response()


@guest.post("/forgot-password")
async def forgot_password(request: ForgotPassword):
    find_guest = CheckGuest(target="CHECK_GUEST",
                            email=request.email)
    response = await guest_email(email=request.email)
    if response is None:
        raise CustomExceptionHandler(message="Admin Not Found",
                                     success=False,
                                     code=status.HTTP_400_BAD_REQUEST,
                                     target="FORGOT-PASSWORD")
    reset_code = str(uuid.uuid1())
    try:
        await create_reset_code(email=request.email, reset_code=reset_code)
    except Exception as Why:
        logger.error("=== ERROR OCCURED IN RESETTING PASSWORD {} =====".format(Why))
        raise CustomExceptionHandler(message="Something went wrong at our end,Please try again later",
                                     code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     success=False,
                                     target="[RESET_PASSWORD]"
                                     )
    return ResponseModel(message="Email has been sent with instructions to reset password",
                         success=True,
                         code=status.HTTP_201_CREATED,
                         data={"code": reset_code}
                         )


@guest.post("/reset-password")
async def reset_password(request: ResetPassword):
    check_token = await check_reset_password_token(request.reset_password_token)
    if not check_token:
        logger.error("======== RESET TOKEN HAS EXPIRED =========")
        raise CustomExceptionHandler(message="Reset password token has expired,please request a new one",
                                     success=False,
                                     code=status.HTTP_404_NOT_FOUND,
                                     target="[RESET_PASSWORD]"
                                     )
    match = check_password_strength(password=request.new_password)
    if not match:
        raise CustomExceptionHandler(message="Password pattern mismatch",
                                     target="Check_Regex_Password",
                                     code=status.HTTP_400_BAD_REQUEST,
                                     success=False
                                     )

    if request.new_password != request.confirm_password:
        raise CustomExceptionHandler(message="Sorry, password didn't match",
                                     success=False,
                                     code=status.HTTP_409_CONFLICT,
                                     target="RESET-PASSWORD")

    new_hashed_password = hash_password(request.new_password)
    try:
        await reset_admin_password(new_hashed_password=new_hashed_password,
                                   email=check_token["email"]
                                   )
        await disable_reset_code(request.reset_password_token, check_token["email"])
    except Exception as Why:
        logger.error("===== EXCEPTION OCCURRED IN RESETTING PASSWORD ========".format(Why))
        raise CustomExceptionHandler(message="Something went wrong at our end,Please try again later",
                                     code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     success=False,
                                     target="[RESET_PASSWORD]"
                                     )
    return ResponseModel(message="Password has been reset successfully.",
                         success=True,
                         code=status.HTTP_200_OK,
                         data={}
                         ).response()


@guest.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    logger.info("====== LOGIN VIA MAIL/PHONE ========")
    success = await guest_registered_with_mail_or_phone(credential=form_data.username)
    if success is None:
        raise CustomExceptionHandler(message="OOPS!,Please Register Yourself",
                                     code=status.HTTP_404_NOT_FOUND,
                                     target="GUEST_LOGIN",
                                     success=False
                                     )

    verify_pass = verify_password(plain_password=form_data.password, hashed_passwrd=success["password"])
    if not verify_pass:
        raise CustomExceptionHandler(message="Please Check your password",
                                     code=status.HTTP_400_BAD_REQUEST,
                                     target="GUEST_LOGIN",
                                     success=False
                                     )
    access_token_expires = jwt_utils.timedelta(minutes=JWT_EXPIRATION_TIME)
    info = jsonable_encoder(success)
    access_token = await jwt_utils.create_access_token(
        data=info,
        expire_delta=access_token_expires
    )
    return {"message": "Successfully Login",
            "code": status.HTTP_201_CREATED,
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "data": {"id": success["id"],
                     "first_name": success["first_name"],
                     "last_name": success["last_name"],
                     "gender": success["gender"],
                     "profile_url": success["profile_url"],
                     "email": success["email"],
                     "phone_number": success["phone_number"]
                     }}


@guest.get("/profile")
async def fetch_admin_info(current_user=Depends(get_current_user)):
    logger.info("======== FETCHING INFORMATION ================")
    return ResponseModel(message="Success",
                         success=True,
                         code=status.HTTP_200_OK,
                         data=current_user
                         )


@guest.patch("/profile")
async def update_guest_profile(guest: UpdateGuest, current_user=Depends(get_current_user)):
    logger.info("UPDATING PROFILE")
    if guest.phone_number is not None:
        success = await guest_registered_with_mail_or_phone(credential=guest.phone_number)
        if success is not None:
            raise CustomExceptionHandler(message="Phone number already registered or Updating Same Number",
                                         code=status.HTTP_404_NOT_FOUND,
                                         target="ADMIN-CHECK-REGISTRATION",
                                         success=False
                                         )
    query_for_update = "UPDATE guest SET "
    WHERE_ID_ADMIN = " WHERE id=:id RETURNING id"
    values_map = {}
    for key in guest:
        if key[1] is None:
            continue
        values_map[key[0]] = key[1]
        query_for_update = query_for_update + key[0] + "".join("=:") + key[0] + ","
    query_for_update = query_for_update.rstrip(",")
    dt = datetime.now(timezone("Asia/Kolkata"))
    query_for_update = query_for_update + ",updated_on='{}'".format(dt)
    query_for_update = query_for_update + WHERE_ID_ADMIN
    values_map["id"] = current_user["id"]
    try:
        success = await update_guest(query=query_for_update, values=values_map)
    except Exception as Why:
        logger.error("========= UNABLE TO UPDATE THE ADMIN BECAUSE =============".format(str(Why)))
        raise CustomExceptionHandler(message="Something Went Wrong, Cannot Update Profile",
                                     code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     success=False,
                                     target=""
                                     )
    find_guest = CheckGuest(target="CHECK_GUEST",
                            id=success)
    return ResponseModel(message="Details Updates Successfully",
                         code=status.HTTP_200_OK,
                         success=True,
                         data=await find_guest.find_guest_by_id()
                         ).response()


@guest.post("/property/favourite")
async def favourite_property(fav: MarkPropertyFavourite, current_user=Depends(get_current_user)):
    logger.info("MARKING PROPERTY FAVOURITE")
    # CHECK IF PROPERTY ID IS THERE AND IT IS IN ACTIVE STATE
    property_information = await find_particular_property_information(fav.property_id)
    if property_information is None:
        raise CustomExceptionHandler(message="No Property Found",
                                     success=False,
                                     target="",
                                     code=status.HTTP_400_BAD_REQUEST
                                     )
    # CHECK IF PROPERTY IS ALREADY ADDED ACTIVE
    fav_property_exist = await check_fav_property_existence(property_id=fav.property_id,
                                                            user_id=current_user["id"]
                                                            )
    if fav_property_exist is not None:
        raise CustomExceptionHandler(message="Property Already Marked as favourite",
                                     code=status.HTTP_409_CONFLICT,
                                     success=False,
                                     target="MARK_FAV_PROPERTY"
                                     )

    success = await add_guest_fav_property(fav={"is_active": True,
                                                "property_id": fav.property_id,
                                                "user_id": current_user["id"]
                                                })
    if success is None:
        raise CustomExceptionHandler(message="Something is wrong with our server,we are working on it.",
                                     code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                     success=False,
                                     target="MARK_FAV_PROPERTY"
                                     )
    return ResponseModel(message="Property Added to favourites",
                         code=status.HTTP_200_OK,
                         success=True,
                         data={}
                         ).response()


@guest.patch("/change-password")
async def change_password(change_password_object: ChangePassword, current_user=Depends(get_current_user)):
    logger.info("======= CHANGING PASSWORD FOR USER {} ==========".format(current_user["first_name"]))
    cred = await get_protected_password(email=current_user["email"])
    valid_cred = verify_password(change_password_object.current_password, cred)
    if not valid_cred:
        logger.error("OOPS!! Current password does not match")
        raise CustomExceptionHandler(message="OOPS!! Your password is incorrect",
                                     code=status.HTTP_409_CONFLICT,
                                     success=False,
                                     target="VERIFY-CURRENT_PASSWORD")
    match = check_password_strength(password=change_password_object.new_password)
    if not match:
        raise CustomExceptionHandler(message="Password pattern mismatch",
                                     target="Check_Regex_Password",
                                     code=status.HTTP_400_BAD_REQUEST,
                                     success=False
                                     )
    if change_password_object.new_password != change_password_object.confirm_password:
        raise CustomExceptionHandler(message="OOPS!! New password and Confirm password does not match",
                                     code=status.HTTP_409_CONFLICT,
                                     success=False,
                                     target="VERIFY-CURRENT_PASSWORD")
    change_password_object.new_password = hash_password(change_password_object.new_password)
    try:
        await guest_change_password(change_password_object, email=current_user["email"])
    except Exception as Why:
        logger.error("ERROR OCCURRED IN CHANGING PASSWORD BECAUSE OF {}".format(Why))
        raise CustomExceptionHandler(message="Something is wrong with our server,we are working on it.",
                                     code=status.HTTP_503_SERVICE_UNAVAILABLE,
                                     success=False,
                                     target="CHANGE_PASSWORD_DB_UPDATE"
                                     )
    else:
        return ResponseModel(message="Password has been updated successfully",
                             code=status.HTTP_200_OK,
                             success=True,
                             data={}
                             ).response()


@guest.get("/property/favourite")
async def fetch_favourite_property(current_user=Depends(get_current_user)):
    logger.info("ADDING PROPERTY AS FAVOURITE")
    return ResponseModel(message="Favourite Properties",
                         code=status.HTTP_200_OK,
                         success=True,
                         data=await find_user_fav_properties(user_id=current_user["id"])
                         ).response()


@guest.delete("/property/favourite")
async def favourite_property(fav: UpdateMarkPropertyFavourite, current_user=Depends(get_current_user)):
    logger.info("REMOVING PROPERTY AS FAVOURITE")
    logger.info("CHECKING IF PROPERTY EXIST ON THE TABLE")
    property_information = await find_particular_property_information(fav.property_id)
    if property_information is None:
        raise CustomExceptionHandler(message="No Property Found",
                                     success=False,
                                     target="",
                                     code=status.HTTP_400_BAD_REQUEST
                                     )
    logger.info("CHECKING IF USER HAS LISTED PROPERTY EARLIER")
    success = await update_guest_fav_property(is_active=fav.is_active,
                                              property_id=fav.property_id,
                                              user_id=current_user["id"]
                                              )
    if success is None:
        raise CustomExceptionHandler(message="Something is wrong with our server,we are working on it.",
                                     code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                     success=False,
                                     target="CANNOT_MARK_PROPERTY_UNFAV"
                                     )
    return ResponseModel(message="Favourites Updated",
                         code=status.HTTP_200_OK,
                         success=True,
                         data=await find_user_fav_properties(user_id=current_user["id"])
                         ).response()
