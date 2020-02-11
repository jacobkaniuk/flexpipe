import os
import sys
from 

class ProductionManager(object):
    def __init__(self, config_file):
        self.config_file = config_file
        self.database_connection = None
        self.database_token = None
        self.database_url = None
        self.use_config_all_projects = False

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
        return

    def create_project(self, project_name):
        """
        Create a new db with name of project name in connected db
        :param project_name: str name of project to be created
        :return: str database path to project
        """
        return

    def update_project(self, project_name, project_settings):
        """
        Update the project config using the provided project settings
        dict holding envars, folder structure, etc.
        :param project_name: str name of project to be created
        :param project_settings: dict config to be set for project
        :return: dict updated project config details
        """
        return

    def set_project_path(self, project, new_project_path):
        """
        Set the bsdr path for the project to use
        ie. /mnt/z/vfx , paths in db /proj1/shots/env_cave/prop_rock
        /mnt/Z/vfx/proj1/shots/env_cave/prop_rock
        :param project: str project to change path on
        :param new_project_path: str new root path for project to be stored
        :return: str project path confirm
        """
        return

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

    def create_shot(self, project, shot, is_single_asset_shot=False):
        """
        Create a shot for the specified project, specify if the shot is
        a single asset ie. VHCL_STEAM_LOCOMOTIVE
        :param project: str project to make changes to
        :param shot: str name of shot to be added to project
        :param is_single_asset_shot: bool:False is this shot going to contain
        only one asset, or will there be many assets in this shot
        :return: str relative db path created for this shot
        """
        return

    def create_asset(self, project, shot):
        """
        Creates an asset sub directory for a shot ie. PROP_TABLE_LARGE
        :param project: str project to make changes to
        :param shot: str name of shot asset will be added to
        :return: str relative db path created for this asset
        """
        return

    @staticmethod
    def get_project_info(project):
        """
        Return the config for this project (envars)
        :param project: str project to get info on
        :return: dict config info for project
        """
        return

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
