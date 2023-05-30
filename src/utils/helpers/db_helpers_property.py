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
    query = "SELECT *FROM booking WHERE (booking_time,departure_time) OVERLAPS ('{}'::timestamp, " \
            "'{}'::timestamp) AND status='CONFIRMED' AND room_id='{}'".format(booking_time,departure_time,room_id)
    return db.fetch_one(query=query)

def room_count(booking_parent_id):
    query = "SELECT DISTINCT room_id FROM booking WHERE booking_parent_id='{}'".format(booking_parent_id)
    return db.fetch_all(query=query)

def particular_room_info(id):
    query = "SELECT id,property_id,room_type,room_size,bed_size_type,number_of_bathrooms,max_occupancy,room_description FROM rooms WHERE id=:id"
    return db.fetch_one(query=query,values={"id":id})


def find_rooms(property_id: int):
    query = "SELECT * FROM rooms WHERE property_id=:property_id"
    return db.fetch_all(query=query, values={"property_id": property_id})


def check_if_room_exist(property_id: int):
    query = "SELECT * FROM rooms WHERE property_id=:property_id"
    return db.fetch_one(query=query, values={"property_id": property_id})


def find_rooms_wise_price(property_id: int):
    query = "SELECT DISTINCT room_type,base_room_price,extra_mattress_price FROM rooms WHERE property_id=:property_id"
    return db.fetch_all(query=query,values={"property_id":property_id})

QUERY_FOR_FINDING_PROPERTY_FACILITY = "SELECT property_facility_map.property_id, facilities.name,facilities.id," \
                                      "facilities.is_active FROM property_facility_map INNER JOIN facilities ON " \
                                      "property_facility_map.facility_id=facilities.id WHERE property_id=:property_id "

def get_facility_of_property(property_id:int):
    return db.fetch_all(query=QUERY_FOR_FINDING_PROPERTY_FACILITY,values={"property_id":property_id})


QUERY_FOR_FINDING_PROPERTY_AMENITY = "SELECT property_amenity_map.property_id, amenties.name,amenties.id," \
                                      "amenties.is_active FROM property_amenity_map INNER JOIN amenties ON " \
                                      "property_amenity_map.amenity_id=amenties.id WHERE property_id=:property_id "

def get_amenity_of_property(property_id:int):
    return db.fetch_all(query=QUERY_FOR_FINDING_PROPERTY_AMENITY,values={"property_id":property_id})
