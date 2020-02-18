from pymongo import MongoClient
from pymongo import errors as pymongoErrors
from pymongo.database import Database

from core_api import production


class ProductionManager(object):
    def __init__(self, config_file):
        self.db_type = config_file
        self.database_connection = None
        self.database_url = None
        self.use_config_all_projects = False
        self.connect_to_database('localhost')

    def parse_config(self):
        """
        Parse the config file and set contents to manager instance
        :return: bool did the contents get parsed properly
        """

    def connect_to_database(self, database_url):
        """
        Connect to the database given
        :param database_url: str
        :return:
        """
        if self.db_type == 'mongodb':
            try:
                mongo_db_client = MongoClient(database_url, port=27017, serverSelectionTimeoutMS=5)
                mongo_db_client.server_info()
                self.database_connection = mongo_db_client
                return mongo_db_client

            except pymongoErrors.ServerSelectionTimeoutError as error:
                print "\nCould not not connect to database: {} at {}".format(
                    self.db_type,
                    database_url
                ), error

    def check_db_connection(self, error_msg=None):
        if error_msg:
            error_msg = "Could not {}. No connection to database established.".format(error_msg)
        if self.database_connection is None:
            raise RuntimeError(error_msg)

    def check_project_exists(self, project_name, project_id=None):
        if not isinstance(project_name, str):
            raise TypeError("Invalid argument type. Project are expected to be provided as ",
                            "type: str, got: {}".format(
                             type(project_name))
            )
        if project_id:
            if not isinstance(project_id, int):
                raise TypeError("Invalid argument type. Project ids are expected to be provided as ",
                                "type: int, got: ".format(
                                    type(project_id))
                                )

        if project_name not in self.database_connection.list_database_names():
            raise pymongoErrors.ConnectionFailure, "Project invalid. Please check project name"

        else:
            return True

    @staticmethod
    def verify_project_type(project, expected):
        if not isinstance(project, expected):
            raise TypeError("Invalid type passed. Got: {} ",
                            "Expected: {}".format(type(project)), type(expected))

    def create_project(self, project):
        """
        Create a new db with name of project name in connected db
        :param project: production.Project name of project database to be created
        :return: str database path to project
        """
        self.check_db_connection("add any projects")
        self.verify_project_type(project, production.Project)

        # don't add project if it already exists
        if project.name in self.database_connection.list_database_names():
            print "\nProject creation failed. Project already exists in database server at: {}".format(
                self.database_connection
            )

        else:
            # TODO create default tables for new project, how are we going to load them in (external config ? )
            init_collections = ['settings', 'shots', 'assets', 'users']
            for collection in init_collections:
                Database(self.database_connection, project.name).create_collection(collection)

            settings = production.remove_namespaces(project.__dict__)
            self.database_connection[project.name]['settings'].insert_one(settings)

        # return database
        return self.database_connection[project.name]

    def update_project(self, project):
        """
        Update the project config using the provided project settings dict
        :param project: production.Project name of project to be created
        :return: database with updated project config details
        """
        self.check_db_connection("update any projects")
        self.check_project_exists(project.name)
        self.verify_project_type(project, production.Project)

        updated_project = production.remove_namespaces(project.__dict__)
        query = {"name": project.name}
        new_value = {"$set": updated_project}
        self.database_connection[project.name]['settings'].update_one(query, new_value)

        return self.database_connection[project.name]

    def get_project_info(self, project_name):
        """
        Return the config for this project (envars)
        :param project_name: str project to get info on
        :return: dict config info for project
        """
        self.check_db_connection(error_msg="gather project info")
        self.check_project_exists(project_name)
        self.verify_project_type(project_name, str)

        # project_dict = self.database_connection[project_name]['settings'].find({'name': project_name})[0]
        return self.database_connection[project_name]['settings'].find({'name': project_name})[0]

    def create_shot(self, project_name, shot, is_single_asset_shot=False):
        """
        Create a shot for the specified project, specify if the shot is
        a single asset ie. VHCL_STEAM_LOCOMOTIVE
        :param project_name: str project to make changes to
        :param shot: production.Shot shot  object to be added to project
        :param is_single_asset_shot: bool:False is this shot going to contain
        only one asset, or will there be many assets in this shot
        :return: str relative db path created for this shot
        """
        self.check_db_connection(error_msg="create shot")
        self.check_project_exists(project_name)
        self.verify_project_type(project_name, str)

        shot_dict = production.remove_namespaces(shot.__dict__)
        query = {'name': shot.name}
        value = {'$set': shot_dict}

        self.database_connection[project_name]['shots'].update_one(query, value, upsert=True)

    def update_shot(self, project_name, shot, is_single_asset_shot=False):
        """
        Same as crate_shot, use this to update the shot info
        """
        self.check_db_connection(error_msg="update shot")
        self.check_project_exists(project_name)
        self.verify_project_type(project_name, str)

        shot_dict = production.remove_namespaces(shot.__dict__)
        query = {'name': shot.name}
        value = {'$set': shot_dict}
        self.database_connection[project_name]['shots'].update_one(query, value)

        return self.database_connection[project_name]['shots']

    def set_project_path(self, project_name, new_project_path):
        """
        Set the bsdr path for the project to use
        ie. /mnt/z/vfx , paths in db /proj1/shots/env_cave/prop_rock
        /mnt/Z/vfx/proj1/shots/env_cave/prop_rock
        :param project_name: str project to change path on
        :param new_project_path: str new root path for project to be stored
        :return: str project path confirm
        """
        self.check_db_connection(error_msg="set project path")
        self.check_project_exists(project_name)
        self.verify_project_type(project_name, str)

        query = {"name": project_name}
        new_value = {"$set": {"data_path": new_project_path}}
        self.database_connection[project_name]['settings'].update_one(query, new_value)

        return self.database_connection[project_name]

    def add_asset_type(self, project, asset_type, asset_path=None):
        """
        Add a new type of asset to the projects list of compatible assets
        :param project: str project to make changes to
        :param asset_type: class type of asset to add to project
        :param asset_path: str path to use for storing these types of assets
        :return: bool was asset successfully added to project config
        """
        return

    def set_asset_type_path(self, project, asset_type, asset_path):
        """
        Set the relative db path for these types of assets
        ie. ( ModelAsset -> /assets/model/lib )
        :param project: str project to make changes to
        :param asset_type: class asset type to change path of
        :param asset_path: str new relative db path
        :return: str new relative db path for asset type
        """
        return

    def create_asset(self, project, shot, asset_name, **kwargs):
        """
        Creates an asset sub directory for a shot ie. PROP_TABLE_LARGE
        :param project: str project to make changes to
        :param shot: str name of shot asset will be added to
        :param asset_name str name of asset which will be created
        :param kwargs any additional attributes to be added to the asset
        :return: objectID newly created asset entry
        """
        self.check_db_connection(error_msg='create asset')
        self.check_project_exists(project.name)
        self.verify_project_type(project, production.Project)

        data = {
            'project': project.name,
            'shot': shot,
            'name': asset_name,
            'validators': [],
            'last_mofidied': None,
            'last_user': None
        }

        # extend our asset if we provide a dict
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            else:
                raise ReferenceError("Found additional field in kwargs. Please use update_asset method instead.")

        return self.database_connection[project.name]['assets'].update({'name': asset_name}, {'$set': data}, upsert=True)

    def update_asset(self, project_name=None, shot=None, asset_name=None, asset_id=None, **kwargs):
        """
        Creates an asset sub directory for a shot ie. PROP_TABLE_LARGE
        :param project_name: str project to make changes to
        :param shot: str name of shot asset will be a 'child' of
        :param asset_name str name of asset which will be updated
        :param asset_id str mongodb objectID to access asset. only need project params if provided
        :param kwargs any additional attributes to be added to the asset
        :return: objectID newly created asset entry
        """
        # TODO make updating assets a global search through all databases (projects) make sure performance does
        #  not take a hit because of this. maybe search with iter->client.list_database_names()->find(ObjectID(id)) ?

        self.check_db_connection(error_msg="update asset")
        if project_name:
            self.verify_project_type(project_name, str)
            self.check_project_exists(project_name)

        if not asset_id:
            asset_id = self.database_connection[project_name]['assets'].find({'name': asset_name})[0]['_id']
        query = {'_id': asset_id}
        data = {'project': project_name, 'shot': shot, 'name': asset_name}
        for key, value in kwargs.items():
            data[key] = value

        if all(arg is not None for arg in [project_name, shot, asset_name]):
            return self.database_connection[project_name]['assets'].update_one(query, {'$set': data})

    def create_user(self, user_name, user_email, user_password,
                    permission_group, region=None, language=None):
        """
        Create user using required parameters
        :param user_name: str Required: user name
        :param user_email: str Required: email for user
        :param user_password: str Required: password for user
        :param permission_group: int permission level (user, supervisor, manager, admin, master)
        :param region: str geographical region
        :param language: str primary/preferred language
        :return: int uid of newly created user
        """
        return
