import psycopg2
from src.utils.logger.logger import logger
from src.constants.utilities import DB_USER, DB_NAME, DB_HOST, DB_PASSWORD, DB_PORT

class DatabaseConfiguration:
    def __init__(self):
        self.connection = None

    def checking_connection(self):
        try:
            # self.connection = psycopg2.connect(database=DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD,
            #                                    port=DB_PORT)
            self.connection = psycopg2.connect(user=DB_USER, host=DB_HOST, password=DB_PASSWORD,database=DB_NAME,
                                               port=DB_PORT)
            logger.info("######### DATABASE CONNECTED, PROCEEDING FURTHER  ###########")
        except Exception as e:
            logger.error("###### CANNOT ABLE TO CONNECT WITH DATABASE WITH EXCEPTION {} ########".format(e))
            raise Exception(e)
        finally:
            logger.info("##### CHECK DB FUNCTION COMPLETED ####")
        return self.connection

    @staticmethod
    def checking_database_connection():
        connect = DatabaseConfiguration().checking_connection()
        if connect is not None:
            connect.autocommit = True
            cur = connect.cursor()
            cur.execute("SELECT datname FROM pg_database;")
            list_database = cur.fetchall()
            database_name = DB_NAME
            if (database_name,) in list_database:
                logger.info("####### DATABASE ALREADY EXIST WITH NAME {} ##########".format(database_name))
            else:
                logger.error("{} DATABASE NOT EXIST".format(database_name))
                sql = '''CREATE database roomshala_admin'''
                cur.execute(sql)
                logger.info("### DATABASE CREATED SUCCESSFULLY ###")
            connect.close()
            logger.info("####### DONE ###########")


