from pymongo import MongoClient
from pymongo import auth
from pymongo.errors import ConnectionFailure


DEFAULT_CONNECTION = "FLEXPIPE_MONGO_CLIENT"


class DatabaseConnection(object):
    def __init__(self):
        self.connection_status = False
        self.connection_state = None
        self.connection_uptime = None
        self.db_client = None
        self.__user_group = None
        self.__user_permissions = None

    def _establish_db_connection(self):
        if not globals().copy().get(DEFAULT_CONNECTION):
            try:
                self.create_new_db_connection()
            except ConnectionFailure as cf:
                print "Could not establish a connection to the database. Aborting. {}".format(cf)

    def create_new_db_connection(self):
        # get user details and connect to db with given creds and set permissions
        pass

    def _set_db_conn_info(self):
        # get the details of the users connection to db
        pass

    def __repr__(self):
        pass