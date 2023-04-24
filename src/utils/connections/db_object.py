from src.constants.utilities import DB_URL
from databases import Database

from src.utils.custom_exceptions.custom_exceptions import DatabaseConnectionError
from src.utils.logger.logger import logger
try:
    logger.info(" ########## GOING FOR CONNECTION ##############")
    # db = Database(DB_URL)
    db = Database(
        "postgres://potgresql:27tsgGwha7FOJaS3nuIKT917IZqjXyyl@dpg-cg7pbdik728uq3pld0a0-a.oregon-postgres.render.com/ro")
except Exception as e:
    logger.error("###### EXCEPTION IN DB_OBJECT IS {} ###########".format(e))
    raise DatabaseConnectionError(message="Error Occur in Database {}".format(e))

#postgres://potgresql:27tsgGwha7FOJaS3nuIKT917IZqjXyyl@dpg-cg7pbdik728uq3pld0a0-a.oregon-postgres.render.com/ro