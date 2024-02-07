from src.utils.connections.db_object import db
from src.utils.helpers.db_queries import QUERY_FOR_FINDING_FEEDBACK, QUERY_FOR_FINDING_BOOKING, \
    QUERY_FOR_FINDING_PROPERTY_AMENITY, QUERY_FOR_FINDING_PROPERTY_FACILITY, QUERY_FOR_ADDING_REVIEW, \
    QUERY_FOR_CREATING_TICKET, QUERY_FOR_OPEN_TICKET, QUERY_FOR_ISSUES


def find_particular_property_information(id: int):
    query = "SELECT id,property_code,property_name,property_type,floor_numbers,property_description," \
            "property_email_id,property_mobile_number,complete_address,locality,landmark,pincode,city,state," \
            "property_docs FROM properties WHERE id=:id AND is_active=:is_active"
    return db.fetch_one(query=query, values={"id": id, "is_active": True})


def find_particular_property_information_comp(id: int):
    query = "SELECT id,property_code,property_name,property_type,floor_numbers,property_description," \
            "property_email_id,property_mobile_number,complete_address,locality,landmark,pincode,city,state," \
            "property_docs FROM properties WHERE id=:id"
    return db.fetch_one(query=query, values={"id": id})


def find_particular_room_information(id: int):
    query = "SELECT * FROM rooms WHERE id=:id"
    return db.fetch_one(query=query, values={"id": id})


def find_room_booking(room_id: int,
                      booking_time,
                      departure_time
                      ):
    query = "SELECT * FROM booking WHERE room_id=:room_id AND booking_time=:booking_time AND departure_time=:departure_time AND status='CONFIRMED'"
    return db.fetch_one(query=query,
                        values={"room_id": room_id, "booking_time": booking_time, "departure_time": departure_time})


def find_room_booking_date(room_id: int,
                           booking_date,
                           departure_date,
                           user_id
                           ):
    query = "SELECT * FROM booking WHERE room_id=:room_id AND booking_date=:booking_date AND " \
            "departure_date=:departure_date AND user_id=:user_id AND status='CONFIRMED' "
    return db.fetch_one(query=query,
                        values={"room_id": room_id, "booking_date": booking_date, "departure_date": departure_date,
                                "user_id": user_id})


def find_middle_booking(booking_time, departure_time, room_id):
    query = "SELECT *FROM booking WHERE (booking_time,departure_time) OVERLAPS ('{}'::timestamp, " \
            "'{}'::timestamp) AND status='CONFIRMED' AND room_id='{}'".format(booking_time, departure_time, room_id)
    return db.fetch_one(query=query)


def room_count(booking_parent_id):
    query = "SELECT DISTINCT room_id FROM booking WHERE booking_parent_id='{}'".format(booking_parent_id)
    return db.fetch_all(query=query)


def particular_room_info(id):
    query = "SELECT id,property_id,room_type,room_size,bed_size_type,number_of_bathrooms,max_occupancy,room_description FROM rooms WHERE id=:id"
    return db.fetch_one(query=query, values={"id": id})


def find_rooms(property_id: int):
    query = "SELECT * FROM rooms WHERE property_id=:property_id"
    return db.fetch_all(query=query, values={"property_id": property_id})


def check_if_room_exist(property_id: int):
    query = "SELECT * FROM rooms WHERE property_id=:property_id"
    return db.fetch_one(query=query, values={"property_id": property_id})


def find_rooms_wise_price(property_id: int):
    query = "SELECT DISTINCT room_type,base_room_price,extra_mattress_price FROM rooms WHERE property_id=:property_id"
    return db.fetch_all(query=query, values={"property_id": property_id})


def get_facility_of_property(property_id: int):
    return db.fetch_all(query=QUERY_FOR_FINDING_PROPERTY_FACILITY, values={"property_id": property_id})


def get_amenity_of_property(property_id: int):
    return db.fetch_all(query=QUERY_FOR_FINDING_PROPERTY_AMENITY, values={"property_id": property_id})


def check_booking_id(booking_id: int):
    return db.fetch_one(query=QUERY_FOR_FINDING_BOOKING, values={"id": booking_id})


def check_if_rating_review_exist(booking_id):
    return db.fetch_one(query=QUERY_FOR_FINDING_FEEDBACK, values={"booking_id": booking_id})


def add_review(details):
    return db.execute(query=QUERY_FOR_ADDING_REVIEW, values={"property_id": details["property_id"],
                                                             "booking_id": details["booking_id"],
                                                             "user_id": details["user_id"],
                                                             "rating": details["rating"],
                                                             "comment": details["comment"],
                                                             "management_response": "",
                                                             "helpful_votes": 0,
                                                             "unhelpful_votes": 0
                                                             })


def check_for_open_tickets(user_id):
    return db.fetch_all(query=QUERY_FOR_OPEN_TICKET, values={"user_id": user_id})


def create_ticket(details):
    return db.execute(query=QUERY_FOR_CREATING_TICKET, values={"user_id": details["user_id"],
                                                               "issue": details["issue"],
                                                               "status": details["status"],
                                                               "comments": details["comments"],
                                                               "addresser": "TEAM_ROOMSHALA",
                                                               "comment_by_addresser":"",
                                                               "created_by": details["email"],
                                                               "updated_by": details["email"]
                                                               })


def fetch_my_issues(user_id):
    return db.fetch_all(query=QUERY_FOR_ISSUES,values={"user_id":user_id})


def find_property_reviews(property_id,rating,sorted_by):
    if rating is not None and sorted_by is not None:
        if sorted_by == "RECENT":
            query = """SELECT rating_review.id,rating_review.rating,rating_review.comment,
            rating_review.management_response,first_NAME,last_name FROM rating_review INNER JOIN guest ON 
            rating_review.user_id=guest.id WHERE rating_review.property_id=:property_id AND rating_review.rating 
            <={}ORDER BY rating_review.date_posted DESC """.format(rating)
        else:
            query = """SELECT rating_review.id,rating_review.rating,rating_review.comment,
                        rating_review.management_response,first_NAME,last_name FROM rating_review INNER JOIN guest ON 
                        rating_review.user_id=guest.id WHERE rating_review.property_id=:property_id AND rating_review.rating 
                        <={} ORDER BY rating_review.date_posted ASC """.format(rating)
        return db.fetch_all(query=query,values={"property_id":property_id})

    else:
        query = """SELECT rating_review.id,rating_review.rating,rating_review.comment,
                               rating_review.management_response,first_NAME,last_name FROM rating_review INNER JOIN guest ON 
                               rating_review.user_id=guest.id WHERE rating_review.property_id=:property_id AND rating_review.rating 
                               >=5 ORDER BY rating_review.date_posted DESC """
        return db.fetch_all(query=query, values={"property_id": property_id})

