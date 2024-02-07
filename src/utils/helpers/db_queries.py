QUERY_FOR_INSERTING_GUEST = """INSERT INTO guest VALUES (nextval('guest_id_seq'), :first_name,:last_name,:gender,
                            :email,:password,:phone_number,:is_active,now() at time zone 'UTC',now() at time zone 'UTC',:profile_url) RETURNING id; """

QUERY_FOR_FINDING_FEEDBACK = "SELECT id,property_id,user_id,rating,comment FROM rating_review WHERE booking_id=:booking_id"

QUERY_FOR_FINDING_BOOKING = "SELECT id,property_id,user_id,status FROM booking WHERE id=:id"



QUERY_FOR_FINDING_PROPERTY_AMENITY = "SELECT property_amenity_map.property_id, amenties.name,amenties.id," \
                                     "amenties.is_active FROM property_amenity_map INNER JOIN amenties ON " \
                                     "property_amenity_map.amenity_id=amenties.id WHERE property_id=:property_id "


QUERY_FOR_FINDING_PROPERTY_FACILITY = "SELECT property_facility_map.property_id, facilities.name,facilities.id," \
                                      "facilities.is_active FROM property_facility_map INNER JOIN facilities ON " \
                                      "property_facility_map.facility_id=facilities.id WHERE property_id=:property_id "

QUERY_FOR_ADDING_REVIEW = """INSERT INTO rating_review VALUES (nextval('rating_review_id_seq'), :property_id,:booking_id,:user_id,
     :rating,:comment,:management_response,:helpful_votes,:unhelpful_votes,now() at time zone 'UTC',now() at time zone 'UTC') RETURNING id; """


QUERY_FOR_CREATING_TICKET = """INSERT INTO guest_ticket_management VALUES (nextval('guest_ticket_management_id_seq'),:user_id,:issue,:status,
 :comments,:addresser,:comment_by_addresser,now() at time zone 'UTC',now() at time zone 'UTC',:created_by,:updated_by) RETURNING id;"""


QUERY_FOR_OPEN_TICKET = "SELECT COUNT(*) FROM guest_ticket_management WHERE user_id=:user_id AND status='OPEN'"


QUERY_FOR_ISSUES = "SELECT * FROM guest_ticket_management WHERE user_id=:user_id ORDER BY created_on DESC"


QUERY_FOR_PROPERTY_FEEDBACK = "SELECT "