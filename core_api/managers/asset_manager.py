from collections import OrderedDict
import logging
from logging import Logger


from pymongo import MongoClient
from pymongo import mongo_client
from pymongo import collection
from pymongo import command_cursor
from pymongo import cursor
from bson import ObjectId
from pymongo import errors


from core_api.assets.base_asset import BaseAsset
from core_api.assets.scene_asset import SceneAsset
from core_api.assets.layout_asset import LayoutAsset
from core_api.assets.image_asset import ImageAsset
from core_api.assets.texture_asset import TextureAsset

# use these keys to instantiate an asset object based on their unique member names.
# When extending, make sure inheritance order is set left->right : child->parent
ASSET_TYPES = OrderedDict({
    'parent_scene': LayoutAsset,
    'image_path': ImageAsset,
    'dcc_type': SceneAsset,
    'windows_path': BaseAsset,
})

PUBLISHED_ASSETS = 'published_assets'


class AssetManager(object):
    def __init__(self):
        super(AssetManager, self).__init__(self)
        self.db_client = MongoClient('localhost')  # TODO pass db server we want to connect to

    def get_published_asset(self, uid=None, project=None, shot=None, asset_type=None,
                            asset_name=None, version=None, prev_versions=None):
        """
        Get an asset by uid, or by providing the proj, shot and asset type,
        or by asset name and version number
        :param uid: int return the asset by its unique id
        :param project: str name of the project db to look in
        :param shot: str name of the shot collection for db to look in
        :param asset_name: str name of asset to be searched for
        :param asset_type: class type of asset to return (ie. ModelAsset, ImageAsset)
        :param version: int version to return. If not exist, raise warning return latest
        :param prev_versions: list assets to return going from latest version
        :return: asset object
        """
        if uid:
            query = ({'_id': ObjectId(uid)})
        for database in self.db_client.list_database_names():
            if self.db_client[database][PUBLISHED_ASSETS].find_one(query):
                return self.db_client[database][PUBLISHED_ASSETS].find_one(query)

        # check all required fields were passed to us
        if not all([project, shot, asset_type, asset_name]):
            raise RuntimeError("Could not generate query to search assets with. "
                               "Please make sure you provide the following: {}{}{}{}".format(
                'project', 'shot', 'asset_type', 'asset_name'
            ))

        query = ({'project': project,
                  'shot': shot,
                  'asset_type': asset_type,
                  'asset_name': asset_name})

        # get back all the results, unfiltered
        results = self.db_client[project][PUBLISHED_ASSETS].find_many(query)

        # return a specific version from our arg
        if version:
            return [r for r in results if int(r['version']) == int(version)]

        # return a list of versions based on our arg
        if prev_versions:
            type_error_msg = "Passed argument did not match expected type. Expected: {} or {} Got {}".format(
                int, list, type(prev_versions))

            if isinstance(prev_versions, int):
                if prev_versions < 0:
                    # get the versions from tail of version list ie. (v008, -3 is passed)
                    # versions 6, 7, 8 will be returned
                    return sorted(results, key=lambda x: x('version'))[-prev_versions]

                elif prev_versions > 0:
                    # get the versions from the head of version list ie.(v005, 3)
                    # versions 1, 2, 3 will be returned
                    return sorted(results, key=lambda x: x('version'))[:prev_versions]
                else:
                    raise ValueError("Invalid value type passed. Please provide either a positive "
                                     "or negative integer for version retrieval.")

            if isinstance(prev_versions, list):
                for v in prev_versions:
                    if not isinstance(v, int):
                        try:
                            v = int(v)
                        except TypeError as t:
                            logging.error("{}. {}".format(type_error_msg, t))
                return [r for r in results if r['version'] in prev_versions]
            else:
                raise TypeError(type_error_msg)

        # return the latest version by default
        return max(results, key=lambda x: x['version'])

    def get_assets_by_type(self, asset_type, project=None, shot=None,):
        """
        Check collections of project db, return all assets of asset type
        :param asset_type: class type of asset to search for
        :param project: str name of project db to search
        :param shot: str name of shot to search
        :return: list asset objects
        """
        query = ({'asset_type': asset_type}) if not shot else ({'asset_type': asset_type, 'shot': shot})
        results = list()
        if project:
            results.append(self.db_client[project][PUBLISHED_ASSETS].find_many(query)['_id'])
        else:
            for project in self.db_client.list_database_names():
                results.append(self.db_client[project][PUBLISHED_ASSETS].find_many(query)['_id'])

        return results

    def get_user_assets(self, uid=None, user_id=None, username=None, project=None, shot=None):
        """
        Return all the user assets which may be passed in by unique key, user id or user
        name. project and show fields can be passed in to limit the filtered results
        :param uid: str unique key of user
        :param user_id: int id of user
        :param username: str use username to search database
        :param project: str project to limit search to
        :param shot: str shot to limit search to
        :return: list asset objects
        """
        if uid:
            # lets make sure the uid we passed in exists
            id = self.db_client['admin']['users'].find_one({'_id': uid})['_id']

        elif user_id:
            # lets make sure the user id we passed in exists
            id = self.db_client['admin']['users'].find_one({'user_id': user_id})['_id']

        elif username:
            # lets make sure the username we passed in exists
            id = self.db_client['admin']['users'].find_one({'username': username})['_id']

        if id is None:
            raise errors.InvalidId, "The user provided does not exist. Please try again."

        query = ({'_id': id})
        if shot:
            query['shot'] = shot

        results = list()

        if project:
            results = self.db_client[project][PUBLISHED_ASSETS].find_many(query)

        else:
            for project in self.db_client.list_database_names():
                results.append(self.db_client[project]['published_asset'].find_many(query))

        representations = list()
        for item in results:
            representations.append(create_asset_representation(item))

        return representations


def create_asset_representation(asset_entry):
    from inspect import getargspec

    if not isinstance(asset_entry, dict):
        try:
            asset_entry = dict(asset_entry)
        except TypeError:
            logging.info("Cannot parse asset entry, invalid type. Expected: {} Got: {}".format(
                dict, type(asset_entry)
            ))

    base_class_dict = {
        'name': asset_entry['name'],
        'uid': asset_entry['_id'],
        'upid': asset_entry['created_by'],
        'publish_time': asset_entry['publish_time'],
        'project': asset_entry['project'],
        'shot': asset_entry['shot'],
        'version': asset_entry['version']
    }

    if asset_entry is None:
        raise ValueError('Could not create asset representation. No valid data found for instantiation.')

    for key in asset_entry:
        if key in ASSET_TYPES:
            asset_class = ASSET_TYPES.get(key)

    init_dict = dict()
    for arg in asset_entry:
        if arg in getargspec(asset_class.__init__):
            init_dict[arg] = asset_entry[arg]

    return asset_class(base_class_dict)


def get_asset_by_database_path(database_path):
    """
    Return the asset by using the database relative path
    :param database_path:
    :return:
    """


