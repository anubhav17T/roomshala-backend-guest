from src.utils.connections.db_object import db


def find_particular_property_information(id: int):
    query = "SELECT id,property_code,property_name,property_type,floor_numbers,property_description," \
            "property_email_id,property_mobile_number,complete_address,locality,landmark,pincode,city,state," \
            "property_docs FROM properties WHERE id=:id AND is_active=:is_active"
    return db.fetch_one(query=query, values={"id": id, "is_active": True})


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


def find_middle_booking(booking_time,departure_time,room_id):
    query = "SELECT *FROM booking WHERE (booking_time,departure_time) OVERLAPS ('{}'::DATE, " \
            "'{}'::DATE) AND status='CONFIRMED' AND room_id='{}'".format(booking_time,departure_time,room_id)
    return db.fetch_one(query=query)

