from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from fastapi.encoders import jsonable_encoder
from src.constants.utilities import JWT_EXPIRATION_TIME
from src.models.feedback import Feedback, Ticket
from src.utils.custom_exceptions.custom_exceptions import CustomExceptionHandler
from src.utils.helpers.db_helpers_property import check_booking_id, check_if_rating_review_exist, add_review, \
    check_for_open_tickets, create_ticket, fetch_my_issues, find_property_reviews
from src.utils.helpers.jwt_utils import get_current_user
from src.utils.logger.logger import logger
from src.utils.response.data_response import ResponseModel

feedback = APIRouter()


@feedback.post("/property/feedback")
async def property_reviews_ratings(feed: Feedback, current_user=Depends(get_current_user)):
    logger.info("======== MARKING REVIEWS AND RATING FOR USER {}".format(current_user["id"]))
    booking_details = await check_booking_id(booking_id=feed.booking_id)
    if booking_details is None:
        raise CustomExceptionHandler(message="OOPS! No booking found",
                                     code=status.HTTP_404_NOT_FOUND,
                                     target="CHECK_BOOKING_ID",
                                     success=False
                                     )
    if booking_details["status"] != "CONFIRMED":
        return ResponseModel(message="Your booking is not Completed yet",
                             code=status.HTTP_200_OK,
                             success=True,
                             data={}
                             ).response()
    else:
        check = await check_if_rating_review_exist(booking_id=feed.booking_id)
        if check is not None:
            return ResponseModel(message="You have already provided us the review",
                                 code=status.HTTP_200_OK,
                                 success=True,
                                 data={"rating": check["rating"],
                                       "comment": check["comment"]
                                       }
                                 ).response()
        else:
            review = await add_review(details={"property_id": booking_details["property_id"],
                                               "booking_id": feed.booking_id,
                                               "user_id": booking_details["user_id"],
                                               "rating": feed.rating,
                                               "comment": feed.comment}
                                      )
            return review


@feedback.post("/property/feedback/votes")
async def vote():
    pass


@feedback.get("/property/feedback/{property_id}")
async def property_feedback(property_id:int,review_type:str = Query(default=None,description="Type of review"),
                            review_rating:int=Query(default=None,description="Rating",ge=0,le=5)):
    logger.info("======= FETCHING PROPERTY REVIEWS ==========")
    if review_type is not None and review_rating is not None:
        if review_type not in ["RECENT","OLDEST"]:
            raise CustomExceptionHandler(message="Please Check review type",
                                         code=status.HTTP_404_NOT_FOUND,
                                         target="CHECK_BOOKING_ID",
                                         success=False
                                         )

        return ResponseModel(message="Please find reviews",
                             code=status.HTTP_200_OK,
                             success=True,
                             data=await find_property_reviews(property_id=property_id,rating=review_rating,sorted_by=review_type)
                             ).response()

    else:
        return ResponseModel(message="Please find reviews",
                             code=status.HTTP_200_OK,
                             success=True,
                             data=await find_property_reviews(property_id=property_id, rating=5,
                                                              sorted_by="RECENT")
                             ).response()



@feedback.post("/issue")
async def ticket(ticket: Ticket, current_user=Depends(get_current_user)):
    logger.info("======= CREATING TICKET =================")
    check = await check_for_open_tickets(user_id=current_user["id"])
    if check[0][0] >= 2:
        return ResponseModel(message="You have more than 2 issues in open state,please contact team roomshala",
                             code=status.HTTP_204_NO_CONTENT,
                             success=True,
                             data={
                             }
                             ).response()
    success = await create_ticket(details={"user_id": current_user["id"],
                                           "issue": ticket.issue_type,
                                           "status": ticket.status,
                                           "comments": ticket.comment,
                                           "email": current_user["email"]
                                           })
    return ResponseModel(message="Your issue is registered successfully, you'll hear us from soon",
                         code=status.HTTP_200_OK,
                         success=True,
                         data={"issue_id": success}
                         ).response()


@feedback.get("/issue")
async def my_issues(current_user=Depends(get_current_user)):
    return ResponseModel(message="Please find your issues",
                         code=status.HTTP_200_OK,
                         success=True,
                         data=await fetch_my_issues(user_id=current_user["id"])
                         ).response()
