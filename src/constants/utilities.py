""" ============= DATABASE CONFIGURATION FILE ================== """
# DB_HOST = "localhost"
# DB_USER = "postgres"
# DB_PASSWORD = "roomshala@123"
# DB_NAME = "roomshala_admin"
DB_PORT = 5432
#ADD DB PASSWORD ON PRODUCTION
# DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
# DB_URL = f"postgresql://{DB_USER}@{DB_HOST}/{DB_NAME}"
DB_HOST ="dpg-cg7pbdik728uq3pld0a0-a.oregon-postgres.render.com"
DB_USER = "potgresql"
DB_PASSWORD = "27tsgGwha7FOJaS3nuIKT917IZqjXyyl"
DB_NAME = "ro"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

EMAIL_REGEX = "^([a-zA-Z0-9_\-\.]+)@([a-zA-Z0-9_\-\.]+)\.([a-zA-Z]{2,5})$"
PHONE_REGEX = "(0/91)?[7-9][0-9]{9}"
JWT_EXPIRATION_TIME = 120 * 24 * 15
JWT_SECRET_KEY = "ef0a1569207bcb280212eb1a0e5948fed64f948049b531574c95813edd8c745c"
JWT_ALGORITHM = "HS256"


BCRYPT_SCHEMA = "bcrypt"



#Roomshala4321