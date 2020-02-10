from pymongo import MongoClient
from pymongo import mongo_client
from pymongo import collection
from pymongo import command_cursor
from pymongo import cursor


class AssetManager(object, parent=None):
    def __init__(self):
        super(AssetManager, self).__init__(self)

    @staticmethod
    def get_published_asset(uid=None, project=None, shot=None, asset_type=None,
                            version=None, prev_versions=None):
        """
        Get an asset by uid, or by providing the proj, shot and asset type,
        or by asset name and version number
        :param uid: int return the asset by its unique id
        :param project: str name of the project db to look in
        :param shot: str name of the shot collection for db to look in
        :param asset_type: class type of asset to return (ie. ModelAsset, ImageAsset)
        :param version: int version to return. If not exist, raise warning return latest
        :param prev_versions: list assets to return going from latest  version
        :return: asset object
        """
        pass

    @staticmethod
    def get_assets_by_type(project, shot, asset_type):
        """
        Check collections of project db, return all assets of asset type
        :param project: str name of project db to search
        :param shot: str name of shot to search
        :param asset_type: class type of asset to search for
        :return: list asset objects
        """

        pass

    @staticmethod
    def get_user_assets(upid, project=None, shot=None):
        """
        Return all the user assets, project and show are optional
        :param upid: int user id to return assets for
        :param project: str project to limit search to
        :param shot: str shot to limit search to
        :return: list asset objects
        """
        return

    @staticmethod
    def get_asset_by_database_path(database_path):
        """
        Return the asset by using the database relative path
        :param database_path:
        :return:
        """


