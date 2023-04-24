from src.utils.connections.db_object import db


def find_particular_property_information(id: int):
    query = "SELECT id,property_code,property_name,property_type,floor_numbers,property_description," \
            "property_email_id,property_mobile_number,complete_address,locality,landmark,pincode,city,state," \
            "property_docs WHERE id=:id AND is_active=:is_active"
    return db.fetch_one(query=query, values={"id": id,"is_active":True})

