import logging
from logging import Logger

from pymongo import MongoClient
from pymongo import errors as pymongoErrors
from pymongo.database import Database
from bson.objectid import ObjectId
from core_api import production
from core_api.conf import PUBLISHED_ASSETS, ASSET_BIN, SETTINGS, SHOTS, PROJECT_USERS


class ConfigurationManager(object):
    #  TODO find library/module for password encryption and decryption
    def __init__(self):
        self.database = MongoClient('localhost')

    def setup_users(self):
        Database(self.database, 'admin').create_collection('users')

    def create_user(self, name, username, user_email, user_password,
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
        user_data = {
            'name': name,
            'username': username,
            'email': user_email,
            # TODO get hashed and salted version of this password before we store it
            'password': user_password,
            'permission_group': permission_group,
            'region': region,
            'language': language
        }

        # only add the user if these 3 fields don't exist
        for attr in ['name', 'username', 'user_email']:
            query = {attr, user_data[attr]}
            if not self.database['admin']['users'].find_one(query):
                return self.database['admin']['users'].insert_one(user_data)
            else:
                raise pymongoErrors.DuplicateKeyError, \
                    "Could not add user to database. Use already exists with fields: {}: {}".format(
                        attr, user_data[attr])

        # TODO create a user id by getting the max user id of all the user docuemnts

    def load_user_data(self, username, password):
        user = self.database['users'].find_one({'username': username})
        if user:
            # TODO make this secure obviously, look into cryptography module
            if user['password'] == password:
                return user


class ProductionManager(object):
    @staticmethod
    def verify_project_type(project, expected):
        if not isinstance(project, expected):
            raise TypeError("Invalid type passed. Got: {} ",
                            "Expected: {}".format(type(project)), type(expected))

    def __init__(self, config_file):
        self.db_type = config_file
        self.db_client = None
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
                self.db_client = mongo_db_client
                return mongo_db_client

            except pymongoErrors.ServerSelectionTimeoutError as error:
                print "\nCould not not connect to database: {} at {}".format(
                    self.db_type,
                    database_url
                ), error

    def check_db_connection(self, error_msg=None):
        if error_msg:
            error_msg = "Could not {}. No connection to database established.".format(error_msg)
        if self.db_client is None:
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

        if project_name not in self.db_client.list_database_names():
            raise pymongoErrors.ConnectionFailure, "Project invalid. Please check project name"

        else:
            return True

    def add_custom_database_entry(self, parent, name, **kwargs):
        self.check_db_connection("add custom collection")

        if not isinstance(name, str):
            try:
                name = str(name)
            except TypeError as err:
                # TODO start using logger
                print "Couldn't add entry to database. {}".format(err)

        if not isinstance(parent, ObjectId):
            if not isinstance(parent, str):
                raise TypeError("Cannot add custom database entry. "
                                "Expected arg of type <str> or <ObjectId>, got: {}".format(type(parent)))

        # check if we're adding in a new database container, or a new collection to a project
        if parent not in self.db_client.list_database_names():
            Database(self.db_client, name).create_collection(parent)
            data = dict()
            for key, value in kwargs.items():
                data[key] = value

            if data:
                pass

    def create_project(self, project):
        """
        Create a new db with name of project name in connected db
        :param project: production.Project name of project database to be created
        :return: str database path to project
        """
        self.check_db_connection("add any projects")
        self.verify_project_type(project, production.Project)

        # don't add project if it already exists
        if project.name in self.db_client.list_database_names():
            print "\nProject creation failed. Project already exists in database server at: {}".format(
                self.db_client
            )

        else:
            # TODO create default tables for new project, how are we going to load them in (external config ? )
            init_collections = [SETTINGS, SHOTS, ASSET_BIN, PROJECT_USERS, PUBLISHED_ASSETS]
            for collection in init_collections:
                Database(self.db_client, project.name).create_collection(collection)

            settings = production.remove_namespaces(project.__dict__)
            self.db_client[project.name][SETTINGS].insert_one(settings)

        # return database
        return self.db_client[project.name]

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
        self.db_client[project.name][SETTINGS].update_one(query, new_value)

        return self.db_client[project.name]

    def get_project_info(self, project_name):
        """
        Return the config for this project (envars)
        :param project_name: str project to get info on
        :return: dict config info for project
        """
        self.check_db_connection(error_msg="gather project info")
        self.check_project_exists(project_name)
        self.verify_project_type(project_name, str)

        # project_dict = self.db_client[project_name][SETTINGS].find({'name': project_name})[0]
        return self.db_client[project_name][SETTINGS].find({'name': project_name})[0]

    def create_shot(self, project_name, shot, is_single_asset_shot=False, **kwargs):
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
        for key, value in kwargs.items():
            shot_dict[key] = value
        query = {'name': shot.name}
        value = {'$set': shot_dict}

        self.db_client[project_name][SHOTS].update_one(query, value, upsert=True)

    def update_shot(self, project_name, shot, is_single_asset_shot=False, **kwargs):
        """
        Same as crate_shot, use this to update the shot info
        """
        self.check_db_connection(error_msg="update shot")
        self.check_project_exists(project_name)
        self.verify_project_type(project_name, str)

        shot_dict = production.remove_namespaces(shot.__dict__)
        for key, value in kwargs.items():
            shot_dict[key] = value
        query = {'name': shot.name}
        value = {'$set': shot_dict}
        self.db_client[project_name][SHOTS].update_one(query, value)

        return self.db_client[project_name][SHOTS]

    def remove_shot(self, project_name=None, shot=None, shot_id=None, cleanup_dir=False):
        """
        Remove the shot container from the database. If cleanup dir is
        set, the files on the storage device will all be deleted as well
        :param project_name: str name of project
        :param shot: str name of shot to be deleted
        :param shot_id: str remove by shot id. if this is provided, this is all we need
        :param cleanup_dir: bool remove files from storage device as well
        :return:
        """
        self.check_db_connection("remove shot")
        if project_name:
            self.check_project_exists(project_name)
            self.verify_project_type(project_name, str)

        try:
            if shot_id:
                shot_id = ObjectId(shot_id)
                query = {'_id': shot_id}

                # search the entire database server for our shot
                for project in self.db_client.list_database_names():
                    result = self.db_client[project][SHOTS].find_one(query)
                    if result is not None:
                        project_name = result['project']
                        shot = result['shot']
                    else:
                        print "Could not find shot with provided id in database: {}".format(shot_id)
                        return False

            if not shot_id:
                if not all([project_name, shot]):
                    raise RuntimeError("Could not create query to search database with. "
                                       "Required arguments not provided: {} or {}, {}".format(
                                        'shot_id', 'project', 'shot'))

                shot_id = self.db_client[project_name][SHOTS].find({'project': project_name,
                                                                      'name': shot})[0]['_id']
                shot_id = ObjectId(shot_id)
                query = {'_id': shot_id}

            if cleanup_dir:
                # remove all asset containers which are from this shot
                self.db_client[project_name][ASSET_BIN].delete_many({'shot': shot})
                # remove all published assets from this shot
                self.db_client[project_name][PUBLISHED_ASSETS].delete_many({'shot': shot})

            if shot_id is not None:
                return self.db_client[project_name][SHOTS].delete_one({'_id': shot_id})
        except IndexError as i:
            print "Did not find shot: {} in project {}. Error: {}".format(shot, project_name, i)

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
        self.db_client[project_name][SETTINGS].update_one(query, new_value)

        return self.db_client[project_name]

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

    def create_asset(self, project, shot, asset_name, status=1, **kwargs):
        """
        Creates an asset sub directory for a shot ie. PROP_TABLE_LARGE
        :param project: str project to make changes to
        :param shot: str name of shot asset will be added to
        :param asset_name str name of asset which will be created
        :param status: int status of the asset (ie. in progress, ready for review, etc.)
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
            'thumbnail': None,
            'users': None,
            'created_by': None,
            'validators': [],
            'last_mofidied': None,
            'last_user': None,
            'status': status
        }

        # extend our asset if we provide a dict
        for key, value in kwargs.items():
            if key not in data:
                data[key] = value
            else:
                raise ReferenceError("Found additional field in kwargs. Please use update_asset method instead.")

        return self.db_client[project.name][ASSET_BIN].update({'name': asset_name}, {'$set': data}, upsert=True)

    def update_asset(self, project_name=None, shot=None, asset_name=None, asset_id=None, **kwargs):
        """
        Creates an asset sub directory for a shot ie. PROP_TABLE_LARGE
        :param project_name: str project to make changes to
        :param shot: str name of shot asset will be a 'child' of
        :param asset_name: str name of asset which will be updated
        :param asset_id: str mongodb objectID to access asset. only need project params if provided
        :param kwargs: any additional attributes to be added to the asset
        :return: objectID newly created asset entry
        """
        # TODO make updating assets a global search through all databases (projects) make sure performance does
        #  not take a hit because of this. maybe search with iter->client.list_database_names()->find(ObjectID(id)) ?

        self.check_db_connection(error_msg="update asset")
        if project_name:
            self.verify_project_type(project_name, str)
            self.check_project_exists(project_name)

        if asset_id:
            asset_id = ObjectId(asset_id)
            query = {'_id': asset_id}
            for project in self.db_client.list_database_names():
                result = self.db_client[project][ASSET_BIN].find_one(query)
                if result:
                    project_name = result['project']
                    shot         = result['shot']
                    asset_name   = result['name']

        else:
            asset_id = self.db_client[project_name][ASSET_BIN].find({'name': asset_name})[0]['_id']

        query = {'_id': asset_id}
        data = {'project': project_name, 'shot': shot, 'name': asset_name}
        for key, value in kwargs.items():
            data[key] = value

        if all(arg is not None for arg in [project_name, shot, asset_name]):
            return self.db_client[project_name][ASSET_BIN].update_one(query, {'$set': data})

    def remove_asset(self, project_name=None, shot=None, asset_name=None, asset_id=None, cleanup_dir=False):
        """
        Remove the shot container from the database. If cleanup dir is
        set, the files on the storage device will all be deleted as well
        :param project_name: str name of project
        :param shot: str name of shot to be deleted
        :param asset_name: str name of asset to delete
        :param asset_id: str
        :param cleanup_dir: bool remove all the files on storage device for this asset
        :return:
        """
        self.check_db_connection("remove asset")
        if project_name:
            self.check_project_exists(project_name)
            self.verify_project_type(project_name, str)

        if asset_id:
            asset_id = ObjectId(asset_id)
            query = {'_id': asset_id}
            #  TODO refactor to one method, return dict
            for project in self.db_client.list_database_names():
                if self.db_client[project][ASSET_BIN].find_one(query):
                    project_name = self.db_client[project][ASSET_BIN].find_one(asset_id)['project']
                else:
                    asset_id = None

        else:
            asset_id = self.db_client[project_name][ASSET_BIN].find({'project': project_name,
                                                                    'shot': shot,
                                                                    'name': asset_name})[0]['_id']

        if asset_id is not None:
            return self.db_client[project_name][ASSET_BIN].delete_one({'_id': asset_id})

    def get_assets_by(self, project, **kwargs):
        """
        General purpose method to return asset bins by provided fields. Use this if you can't get the result from
         other methods in this class, as this may return quite a lot the fewer fields you give it to filter by
        :param project: str name of project we want to search in
        :param kwargs: dict additional keyword arguments we can use as filters on query
        :return: list dicts with info of asset bins
        """
        query = dict()

        for key, value in kwargs.items():
            if key not in query:
                query.update({key: value})

        return [i for i in self.db_client[project][ASSET_BIN].find(query)]

    def get_assets_by_status(self, status, project_name=None, shot=None, asset_name=None, **kwargs):
        """
        Creates an asset sub directory for a shot ie. PROP_TABLE_LARGE
        :param status: int status of asset to search for (ie. ready for review, approved, etc.)
        :param project_name: str project to make changes to
        :param shot: str name of shot asset will be a 'child' of
        :param asset_name: str name of asset which will be updated
        :param kwargs: any additional attributes to be added to the asset
        :return: objectID newly created asset entry
        """

        self.check_db_connection(error_msg="update asset")
        if project_name:
            self.verify_project_type(project_name, str)
            self.check_project_exists(project_name)

        query = dict()
        for key, value in {'status': status, 'project': project_name, 'shot': shot, 'name': asset_name}.items():
            if value is not None:
                query.update({key: value})

        # extend our asset if we provide a dict
        for key, value in kwargs.items():
            if key not in query:
                query[key] = value
            else:
                raise ReferenceError("Found additional field in kwargs. Please use update_asset method instead.")

        return self.db_client[project_name][ASSET_BIN].find(query)
