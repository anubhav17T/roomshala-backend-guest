from src.models.guest import ChangePassword
from src.utils.connections.db_object import db
from src.utils.helpers.db_queries import QUERY_FOR_INSERTING_GUEST
from src.utils.helpers.misc import modify_docs
from src.utils.logger.logger import logger
from datetime import datetime
from pytz import timezone


def guest_id(id):
    query = "select * from guest where id=:id"
    try:
        return db.fetch_one(query=query, values={"id": id})
    except Exception as Why:
        raise Exception("Something Went Wrong {}".format(Why))


def guest_email(email):
    query = "select * from guest where email=:email"
    try:
        return db.fetch_one(query=query, values={"email": email})
    except Exception as Why:
        raise Exception("Something Went Wrong {}".format(Why))


def guest_phone_number(phone_number):
    query = "select * from guest where phone_number=:phone_number"
    try:
        return db.fetch_one(query=query, values={"phone_number": phone_number})
    except Exception as Why:
        raise Exception("Something Went Wrong {}".format(Why))


def add_guest(guest):
    try:
        logger.info("===== CREATING GUEST ENTRY ============")
        return db.execute(QUERY_FOR_INSERTING_GUEST, values={"first_name": guest["first_name"],
                                                             "last_name": guest["last_name"],
                                                             "gender": guest["gender"],
                                                             "email": guest["email"],
                                                             "password": guest["password"],
                                                             "phone_number": guest["phone_number"],
                                                             "is_active": True,
                                                             "profile_url": guest["profile_url"]
                                                             })
    except Exception as Why:
        logger.error("==== ERROR IN ADDING GUEST DUE TO {} ===".format(Why))
        return None


def update_guest(query, values):
    try:
        logger.info("###### DB METHOD UPDATE ADMIN STATUS IS CALLED #########")
        return db.execute(query=query, values=values)
    except Exception as e:
        logger.error("###### SOMETHING WENT WRONG IN UPDATE ADMIN METHOD WITH {} #########".format(e))
    finally:
        logger.info("###### DB METHOD FOR UPDATE_ADMIN UPDATE IS FINISHED ##########")


def get_protected_password(email: str):
    query = "SELECT password FROM guest WHERE email=:email"
    return db.execute(query=query, values={"email": email})


def guest_change_password(change_password_object: ChangePassword, email: str):
    query = "UPDATE admin SET password=:password,updated_on=:updated_on WHERE email=:email"
    logger.info("####### CHANGING USER PASSWORD ##########")
    try:
        return db.execute(query, values={"password": change_password_object.new_password, "email": email,
                                         "updated_on": datetime.now()})
    except Exception as e:
        logger.error("##### EXCEPTION IN CHANGING PASSWORD OF USER IS {}".format(e))


def create_reset_code(email: str, reset_code: str):
    try:
        query = """INSERT INTO guest_code VALUES (nextval('guest_code_id_seq'),:email,:reset_code,now() at time zone 'UTC',
        '1') """
        logger.info("#### PROCEEDING FURTHER FOR THE EXECUTION OF QUERY")
        return db.execute(query, values={"email": email, "reset_code": reset_code})
    except Exception as e:
        logger.error("##### EXCEPTION IN create_reset_code FUNCTION IS {}".format(e))
    finally:
        logger.info("#### create_reset_code FUNCTION COMPLETED ####")


def check_reset_password_token(reset_password_token: str):
    try:
        query = """SELECT * FROM guest_code WHERE status='1' AND reset_code=:reset_password_token AND expired_in >= now() AT TIME 
        ZONE 'UTC' - INTERVAL '10 minutes' """
        logger.info("#### PROCEEDING FURTHER FOR THE EXECUTION OF QUERY")
        return db.fetch_one(query, values={"reset_password_token": reset_password_token})
    except Exception as e:
        logger.error("##### EXCEPTION IN check_reset_password_token FUNCTION IS {}".format(e))
    finally:
        logger.info("#### check_reset_password_token FUNCTION COMPLETED ####")


def reset_admin_password(new_hashed_password: str, email: str):
    try:
        query = """ UPDATE guest SET password=:password WHERE email=:email """
        logger.info("#### PROCEEDING FURTHER FOR THE EXECUTION OF QUERY")
        return db.execute(query, values={"password": new_hashed_password, "email": email})
    except Exception as e:
        logger.error("##### EXCEPTION IN reset_password_user FUNCTION IS {}".format(e))
    finally:
        logger.info("#### reset_password_user FUNCTION COMPLETED ####")


def disable_reset_code(reset_password_token: str, email: str):
    query = "UPDATE guest_code SET status='9' WHERE status='1' AND reset_code=:reset_code AND email=:email"
    try:
        return db.execute(query, values={"reset_code": reset_password_token, "email": email})
    except Exception as e:
        logger.error("#### EXCEPTION IN DISABLE_RESET_CODE IS {}".format(e))
    finally:
        logger.info("#### disable_reset_password_user FUNCTION COMPLETED ####")


def guest_registered_with_mail_or_phone(credential: str):
    query = "SELECT * FROM guest WHERE email=:email OR phone_number=:phone_number"
    return db.fetch_one(query=query, values={"email": credential, "phone_number": credential})


def find_black_list_token(token: str):
    query = "SELECT * FROM guest_blacklists WHERE token=:token"
    try:
        return db.fetch_one(query, values={"token": token})
    except Exception as e:
        logger.error("####### EXCEPTION IN FIND_BLACK_LIST_TOKEN FUNCTION IS = {}".format(e))
    finally:
        logger.info("#### find_black_list_token FUNCTION COMPLETED ####")


def find_exist_guest(email: str):
    query = "select * from guest where email=:email"
    try:
        return db.fetch_one(query=query, values={"email": email})
    except Exception as Why:
        raise Exception("Something Went Wrong {}".format(Why))


def check_fav_property_existence(property_id: int, user_id):
    query = "SELECT * FROM guest_property_fav WHERE property_id=:property_id AND user_id=:user_id"
    try:
        return db.fetch_one(query=query, values={"property_id": property_id, "user_id": user_id})
    except Exception as e:
        logger.error("##### EXCEPTION IN CHECK_PROPERTY_FAV FUNCTION IS {}".format(e))
    finally:
        logger.info("#### CHECK_PROPERTY_FAV FUNCTION COMPLETED ####")


def add_guest_fav_property(fav):
    query = """INSERT INTO guest_property_fav VALUES (nextval('guest_property_fav_id_seq'),:property_id,:user_id,:is_active,now() at time zone 'UTC',now() at time zone 'UTC') RETURNING id; """
    try:
        logger.info("#### PROCEEDING FURTHER FOR THE EXECUTION OF QUERY")
        return db.execute(query,
                          values={"property_id": fav["property_id"], "user_id": fav["user_id"],
                                  "is_active": fav["is_active"]})
    except Exception as e:
        logger.error("##### EXCEPTION IN ADD_GUEST_FAV FUNCTION IS {}".format(e))
    finally:
        logger.info("#### ADD_GUEST_FAV FUNCTION COMPLETED ####")


def update_guest_fav_property(is_active, property_id, user_id):
    query = "UPDATE guest_property_fav SET is_active=:is_active Where property_id=:property_id AND user_id=:user_id RETURNING id;"
    try:
        return db.execute(query, values={"property_id": property_id, "is_active": is_active, "user_id": user_id})
    except Exception as e:
        logger.error("#### EXCEPTION IN MARKING GUEST PROPERTY FAV IS {}".format(e))
    finally:
        logger.info("#### GUEST PROPERTY FAV FUNCTION COMPLETED ####")


def find_user_fav_properties(user_id):
    query = """SELECT guest_property_fav.id,user_id,property_id,guest_property_fav.is_active,guest_property_fav.created_on,guest_property_fav.updated_on,
            properties.property_name,property_type,property_description,property_email_id,complete_address,
            locality,landmark,pincode,city,state,property_docs FROM guest_property_fav INNER JOIN  properties ON guest_property_fav.property_id=properties.id WHERE guest_property_fav.user_id=:user_id"""
    # query = "SELECT * FROM guest_property_fav WHERE user_id=:user_id"
    return db.fetch_all(query=query, values={"user_id": user_id})


def find_fav_property_exist(property_id, user_id):
    query = "SELECT * guest_property_fav WHERE user_id=:user_id AND property_id-:property_id"
    try:
        return db.execute(query, values={"property_id": property_id, "user_id": user_id})
    except Exception as e:
        logger.error("#### EXCEPTION IN MARKING GUEST PROPERTY FAV IS {}".format(e))
    finally:
        logger.info("#### GUEST PROPERTY FAV FUNCTION COMPLETED ####")


def find_booking(id):
    query = "SELECT id,booking_date,booking_time,departure_date,departure_time,adults,children,special_requirement," \
            "booking_base_price,gst_percentage,gst_amount,booking_final_amount,status,created_on,updated_on,created_by,updated_by FROM booking WHERE id=:id "
    return db.fetch_one(query=query,
                        values={"id": id})


def find_booking_based_parent_id(booking_parent_id):
    query = "SELECT * FROM booking WHERE booking_parent_id=:booking_parent_id"
    return db.fetch_all(query=query,
                        values={"booking_parent_id": booking_parent_id})


async def create_booking(book, property, price_distribution, user_info, booking_parent_id):
    async with db.transaction():
        transaction = await db.transaction()
        query = """INSERT INTO booking VALUES (nextval('booking_id_seq'),:booking_parent_id,:property_id,:room_id,:user_id,:booking_date,:booking_time,:departure_date,
            :departure_time,:adults,:children,:special_requirement,:booking_base_price,:number_of_nights,:number_of_rooms,:number_of_extra_guests,:extra_mattress_price,
            :billed_extra_mattress_amount,:billed_base_amount,:billed_gst_amount,:billed_total_amount,:is_booked_for_someone_else,:guest_details,:status,now() at time zone 'UTC',now() at time zone 'UTC',:created_by,:updated_by) RETURNING id; """
        try:
            logger.info("#### PROCEEDING FURTHER FOR THE EXECUTION OF QUERY")
            book.guest_details = modify_docs(dict(book.guest_details))
            for i in book.room_id:
                booking_id = await db.execute(query,
                                              values={"booking_parent_id": booking_parent_id,
                                                      "property_id": property["id"],
                                                      "room_id": i,
                                                      "user_id": user_info["id"],
                                                      "booking_date": book.booking_date,
                                                      "booking_time": book.booking_time,
                                                      "departure_date": book.departure_date,
                                                      "departure_time": book.departure_time,
                                                      "adults": book.adults,
                                                      "children": book.children,
                                                      "special_requirement": book.special_requirement,
                                                      "booking_base_price": book.booking_base_price,
                                                      "number_of_nights": price_distribution["number_of_nights"],
                                                      "number_of_rooms": book.rooms,
                                                      "number_of_extra_guests": price_distribution[
                                                          "number_of_extra_guests"],
                                                      "extra_mattress_price": price_distribution[
                                                          "extra_mattress_price"],
                                                      "billed_extra_mattress_amount": price_distribution[
                                                          "billed_extra_mattress_amount"],
                                                      "billed_base_amount": price_distribution["billed_base_amount"],
                                                      "billed_gst_amount": price_distribution["billed_gst_amount"],
                                                      "is_booked_for_someone_else": book.is_booked_for_someone_else,
                                                      "billed_total_amount": price_distribution["billed_total_amount"],
                                                      "guest_details": book.guest_details,
                                                      "status": book.status,
                                                      "created_by": user_info["email"],
                                                      "updated_by": user_info["email"]
                                                      })
            logger.info("== SUCCESS IN BOOKING TABLE ======")
        except Exception as Why:
            logger.error("######### ERROR IN THE QUERY BECAUSE {} ".format(Why))
            logger.info("########## ROLLING BACK TRANSACTIONS #################")
            await transaction.rollback()
            return False, ""
        else:
            logger.info("##### ALL WENT WELL COMMITTING TRANSACTION ########")
            await transaction.commit()
            logger.info("###### TRANSACTION COMMITTED AND SUCCESS TRUE #######")
            return True, booking_parent_id


def find_booking_for_guest(booking_parent_id, user_id):
    query = """SELECT DISTINCT ON (booking_parent_id) * FROM booking WHERE user_id=:user_id AND booking_parent_id='{}'
    ORDER BY booking_parent_id""".format(booking_parent_id)
    # query = "SELECT * FROM booking WHERE booking_parent_id=:booking_parent_id AND user_id=:user_id "
    return db.fetch_one(query=query,
                        values={"user_id": user_id})


def update_booking(user, booking_parent_id):
    query = "UPDATE booking SET status=:status,updated_on=:updated_on,updated_by=:updated_by WHERE booking_parent_id=:booking_parent_id RETURNING id;"
    dt = datetime.now(timezone("Asia/Kolkata"))

    return db.execute(query=query,
                      values={"status": "CANCELLED", "updated_on": dt.now(), "updated_by": user["email"],
                              "booking_parent_id": booking_parent_id
                              })


def find_upcoming_booking(status, time, user_id):
    if status == "ALL":
        # TODO: NEED TO ADD COMPLETE ATTRIUTES
        query = "SELECT DISTINCT ON (booking_parent_id) booking.id,booking.property_id,booking.booking_parent_id,booking.room_id,booking.user_id,booking.booking_date," \
                "booking.booking_time,booking.departure_date,booking.departure_time,booking.adults,booking.children," \
                "booking.special_requirement,booking.booking_base_price,booking.number_of_nights," \
                "booking.billed_total_amount,booking.number_of_rooms,booking.number_of_extra_guests," \
                "booking.extra_mattress_price,booking.billed_extra_mattress_amount,booking.billed_base_amount,booking.billed_gst_amount,booking.billed_total_amount," \
                "booking.status,booking.created_on,booking.updated_on,booking.guest_details," \
                "booking.created_by,booking.updated_by,rooms.room_type,rooms.bed_size_type,rooms.number_of_bathrooms,rooms.room_size,rooms.bed_size_type," \
                "rooms.max_occupancy,rooms.days,rooms.room_description FROM booking,rooms WHERE " \
                "booking.room_id=rooms.id AND booking.user_id=:user_id AND booking.booking_time >='{}' ORDER BY booking_parent_id,booking.updated_on DESC".format(time)
        # query = "SELECT * FROM booking WHERE user_id=:user_id AND booking_time >='{}'".format(time)
        return db.fetch_all(query=query, values={"user_id": user_id})
    else:
        # TODO: NEED TO ADD COMPLETE ATTRIUTES
        query = "SELECT DISTINCT ON (booking_parent_id) booking.id,booking.property_id,booking.booking_parent_id,booking.room_id,booking.user_id,booking.booking_date," \
                "booking.booking_time,booking.departure_date,booking.departure_time,booking.adults,booking.children," \
                "booking.special_requirement,booking.booking_base_price,booking.number_of_nights," \
                "booking.billed_total_amount,booking.number_of_rooms,booking.number_of_extra_guests," \
                "booking.extra_mattress_price,booking.billed_extra_mattress_amount,booking.billed_base_amount,booking.billed_gst_amount,booking.billed_total_amount," \
                "booking.status,booking.created_on,booking.updated_on,booking.guest_details," \
                "booking.created_by,booking.updated_by,rooms.room_type,rooms.bed_size_type,rooms.number_of_bathrooms," \
                "rooms.max_occupancy,rooms.days,rooms.room_description FROM booking,rooms WHERE " \
                "booking.room_id=rooms.id AND booking.user_id=:user_id AND status=:status AND booking.booking_time >='{}' ORDER BY booking_parent_id,booking.updated_on DESC".format(time)

        return db.fetch_all(query=query, values={"status": status, "user_id": user_id})


def find_previous_booking(status, time, user_id):
    if status == "ALL":
        # TODO: NEED TO ADD COMPLETE ATTRIUTES
        query = "SELECT DISTINCT ON (booking_parent_id) booking.id,booking.property_id,booking.booking_parent_id,booking.room_id,booking.user_id,booking.booking_date," \
                "booking.booking_time,booking.departure_date,booking.departure_time,booking.adults,booking.children," \
                "booking.special_requirement,booking.booking_base_price,booking.number_of_nights," \
                "booking.billed_total_amount,booking.number_of_rooms,booking.number_of_extra_guests," \
                "booking.extra_mattress_price,booking.billed_extra_mattress_amount,booking.billed_base_amount,booking.billed_gst_amount,booking.billed_total_amount," \
                "booking.status,booking.created_on,booking.updated_on,booking.guest_details," \
                "booking.created_by,booking.updated_by,rooms.room_type,rooms.bed_size_type,rooms.number_of_bathrooms,rooms.room_size,rooms.bed_size_type," \
                "rooms.max_occupancy,rooms.days,rooms.room_description FROM booking,rooms WHERE " \
                "booking.room_id=rooms.id AND booking.user_id=:user_id AND booking.booking_time <='{}' ORDER BY booking_parent_id,booking.updated_on DESC".format(time)
        # query = "SELECT * FROM booking WHERE user_id=:user_id AND booking_time >='{}'".format(time)
        return db.fetch_all(query=query, values={"user_id": user_id})
    else:
        # TODO: NEED TO ADD COMPLETE ATTRIUTES
        query = "SELECT DISTINCT ON (booking_parent_id) booking.id,booking.property_id,booking.booking_parent_id,booking.room_id,booking.user_id,booking.booking_date," \
                "booking.booking_time,booking.departure_date,booking.departure_time,booking.adults,booking.children," \
                "booking.special_requirement,booking.booking_base_price,booking.number_of_nights," \
                "booking.billed_total_amount,booking.number_of_rooms,booking.number_of_extra_guests," \
                "booking.extra_mattress_price,booking.billed_extra_mattress_amount,booking.billed_base_amount,booking.billed_gst_amount,booking.billed_total_amount," \
                "booking.status,booking.created_on,booking.updated_on,booking.guest_details," \
                "booking.created_by,booking.updated_by,rooms.room_type,rooms.bed_size_type,rooms.number_of_bathrooms," \
                "rooms.max_occupancy,rooms.days,rooms.room_description FROM booking,rooms WHERE " \
                "booking.room_id=rooms.id AND booking.user_id=:user_id AND status=:status AND booking.booking_time <='{}' ORDER BY booking_parent_id,booking.updated_on DESC".format(
            time)
        return db.fetch_all(query=query, values={"status": status, "user_id": user_id})


def find_base_room_price(property_id):
    query = "SELECT base_room_price FROM rooms WHERE property_id=:property_id"
    return db.fetch_one(query=query, values={"property_id": property_id})


def find_all_cancelled_booking(user_id):
    query = "SELECT DISTINCT ON (booking_parent_id) booking.id,booking.property_id,booking.booking_parent_id,booking.room_id,booking.user_id,booking.booking_date," \
            "booking.booking_time,booking.departure_date,booking.departure_time,booking.adults,booking.children," \
            "booking.special_requirement,booking.booking_base_price,booking.number_of_nights," \
            "booking.billed_total_amount,booking.number_of_rooms,booking.number_of_extra_guests," \
            "booking.extra_mattress_price,booking.billed_extra_mattress_amount,booking.billed_base_amount,booking.billed_gst_amount,booking.billed_total_amount," \
            "booking.status,booking.created_on,booking.updated_on,booking.guest_details," \
            "booking.created_by,booking.updated_by,rooms.room_type,rooms.bed_size_type,rooms.number_of_bathrooms,rooms.room_size,rooms.bed_size_type," \
            "rooms.max_occupancy,rooms.days,rooms.room_description FROM booking,rooms WHERE " \
            "booking.room_id=rooms.id AND booking.user_id=:user_id AND status=:status ORDER BY booking_parent_id,booking.updated_on DESC"
    # query = "SELECT * FROM booking WHERE user_id=:user_id AND booking_time >='{}'".format(time)
    return db.fetch_all(query=query, values={"user_id": user_id,"status":"CANCELLED"})