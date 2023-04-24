from src.models.guest import ChangePassword
from src.utils.connections.db_object import db
from src.utils.helpers.db_queries import QUERY_FOR_INSERTING_GUEST
from src.utils.logger.logger import logger
from datetime import datetime


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
        return db.execute(QUERY_FOR_INSERTING_GUEST, values={"first_name": guest.first_name,
                                                             "last_name": guest.last_name,
                                                             "gender": guest.gender,
                                                             "email": guest.email,
                                                             "password": guest.password,
                                                             "phone_number": guest.phone_number,
                                                             "is_active": True
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


def add_guest_fav_property(fav):
    query = """INSERT INTO guest_property_fav VALUES (nextval('guest_property_fav_id_seq'),:property_id,user_id,is_active,now() at time zone 'UTC',now() at time zone 'UTC',
            '1') """
    try:
        logger.info("#### PROCEEDING FURTHER FOR THE EXECUTION OF QUERY")
        return db.execute(query,
                          values={"property_id": fav.property_id, "user_id": fav.user_id, "is_active": fav.is_active})
    except Exception as e:
        logger.error("##### EXCEPTION IN create_reset_code FUNCTION IS {}".format(e))
    finally:
        logger.info("#### create_reset_code FUNCTION COMPLETED ####")


def update_guest_fav_property(is_active,id):
    query = "UPDATE guest_property_fav SET is_active=:is_active Where id=:id"
    try:
        return db.execute(query, values={"id": id, "is_active": is_active})
    except Exception as e:
        logger.error("#### EXCEPTION IN MARKING GUEST PROPERTY FAV IS {}".format(e))
    finally:
        logger.info("#### GUEST PROPERTY FAV FUNCTION COMPLETED ####")
