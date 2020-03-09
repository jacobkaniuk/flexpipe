from collections import OrderedDict
import logging
from logging import Logger
import warnings

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


logging.basicConfig()


# use these keys to instantiate an asset object based on their unique member names.
# When extending, make sure inheritance order is set left->right : child->parent
ASSET_TYPES = OrderedDict({
    'parent_scene': LayoutAsset,
    'uv_method': TextureAsset,
    'colorspace': ImageAsset,
    'dcc_type': SceneAsset,
    'windows_path': BaseAsset,
})

PUBLISHED_ASSETS = 'published_assets'


class AssetManager(object):
    def __init__(self):
        super(AssetManager, self).__init__()
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
                print "Searching in project: ", database
                if self.db_client[database][PUBLISHED_ASSETS].find_one(query):
                    return create_asset_representation(self.db_client[database][PUBLISHED_ASSETS].find_one(query))
            print "Could not find asset with specified id: {}".format(uid)
            return False

        # check all required fields were passed to us
        if not all([project, shot, asset_type, asset_name]):
            raise RuntimeError("Could not generate query to search assets with. "
                               "Please make sure you provide the following: {}, {}, {}, {}".format(
                                'project', 'shot', 'asset_type', 'asset_name'))

        query = ({'name': asset_name,
                  'project': project,
                  'shot': shot,
                  'asset_type': asset_type})

        # get back all the results, unfiltered
        results = self.db_client[project][PUBLISHED_ASSETS].find(query)
        result_count = self.db_client[project][PUBLISHED_ASSETS].count_documents(query)

        # return a specific version from our arg
        if version:
            if not isinstance(version, int):
                raise TypeError("Could not make result version query. Wrong type provided. Expected: {}. Got: {}".format
                                (int, type(version)))

            if result_count <= 0:
                print "Didn't find any asset with provided attributes."
                return False

            if version > 0:
                # get the version based on the exact number that we pass in ie(version=3 will return version 3 if exist)
                for result in results:
                    if int(result['version']) == int(version):
                        return create_asset_representation(result)

            if version < 0:
                # get the version n versions away from latest version (ie. version=-2 will return second last result)
                versions = sorted(results, key=lambda x: int(x['version']))[version:]
                return create_asset_representation(versions[version:][0])  # pass result as dict not list

            print "Did not find any asset with specified field in results: Version {}".format(version)
            return False

        # return a list of versions based on our arg
        if prev_versions:
            type_error_msg = "Passed argument did not match expected type. Expected: {} or {} Got {}".format(
                int, list, type(prev_versions))

            if isinstance(prev_versions, int):
                if prev_versions < 0:
                    # get the versions from tail of version list ie. (v008, -3 is passed)
                    # versions 6, 7, 8 will be returned
                    sorted_results = sorted(results, key=lambda x: int(x['version']))[prev_versions:]
                    print prev_versions
                    asset_reps = list()
                    for item in sorted_results:
                        asset_reps.append(create_asset_representation(item))

                    return asset_reps

                elif prev_versions > 0:
                    # get the versions from the head of version list ie.(v005, 3)
                    # versions 1, 2, 3 will be returned
                    sorted_results = sorted(results, key=lambda x: int(x['version']))[:prev_versions]
                    asset_reps = list()
                    for item in sorted_results:
                        asset_reps.append(create_asset_representation(item))

                    return asset_reps

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
        print 'Returning latest version of asset'
        return create_asset_representation(max(results, key=lambda x: x['version']))

    def get_assets_by_type(self, asset_type, project=None, shot=None,):
        """
        Check collections of project db, return all assets of asset type
        :param asset_type: str type of asset to search for
        :param project: str name of project db to search
        :param shot: str name of shot to search
        :return: list asset objects
        """
        if not isinstance(asset_type, str):
            if asset_type not in ASSET_TYPES.values():
                raise TypeError("Wrong type passed as asset type. Expected {} or {}, got {}".format(
                    str, BaseAsset, type(asset_type)
                ))
            asset_type = asset_type.__name__
            print asset_type

        query = ({'asset_type': asset_type}) if not shot else ({'asset_type': asset_type, 'shot': shot})
        results = list()
        if project:
            for result in self.db_client[project][PUBLISHED_ASSETS].find(query):
                results.append(result)
        else:
            for project in self.db_client.list_database_names():
                for result in self.db_client[project][PUBLISHED_ASSETS].find(query):
                    results.append(result)

        assets = list()
        for result in results:
            assets.append(create_asset_representation(result))
        return assets

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
        # use one any of these arguments to get the user ObjectId
        if uid:
            result = self.db_client['admin']['users'].find_one({'_id': ObjectId(uid)})
            if result:
                uid = result['_id']
            else:
                uid = None

        for item in [user_id, username]:
            result = self.db_client['admin']['users'].find_one({str(item): item})
            if result:
                uid = result['_id']
                break

        if uid is None:
            print "Could not find any user from the provided fields: " \
                  "\n\t-uid: {}\n\t-user_id: {}\n\t-username: {}\n".format(uid, user_id, username)
            return

        # use our users ObjectId to find assets
        query = ({'created_by': ObjectId(uid)})

        # lets filter out for only the specified shots as well
        if shot:
            query['shot'] = shot

        results = list()
        representations = list()

        if project:
            results = self.db_client[project][PUBLISHED_ASSETS].find(query)

        else:
            for project in self.db_client.list_database_names():
                for result in self.db_client[project][PUBLISHED_ASSETS].find(query):
                    results.append(result)

        for item in results:
            representations.append(create_asset_representation(item))

        return representations


def create_asset_representation(asset_entry):
    from inspect import getargspec

    if not isinstance(asset_entry, dict):
        raise TypeError("Cannot parse asset entry, invalid type. Expected: {} Got: {}".format(
            dict, type(asset_entry)))

    if asset_entry is None:
        raise ValueError('Could not create asset representation. No valid data found for instantiation.')

    # use this dict to pass in the values for our BaseAsset class
    base_class_dict = OrderedDict(
        name=asset_entry['name'],
        uid=asset_entry['_id'],
        upid=asset_entry['created_by'],
        publish_time=asset_entry['publish_time'],
        project=asset_entry['project'],
        shot=asset_entry['shot'],
        version=asset_entry['version']
    )

    # lets figure out which class we should instance if we a specific field in the asset entry
    asset_class = None
    for key in asset_entry:
        if key in ASSET_TYPES:
            asset_class = ASSET_TYPES.get(key)

    if asset_class is None:
        raise KeyError("Could not find asset type to instance from support classes. Please make sure "
                       "you are passing in the correct data. Aborting...\n")

    class_dict = OrderedDict()
    for arg in asset_entry:
        # if we find that this arg is found in the class constructor, add it to our dict
        if arg in getargspec(asset_class.__init__).args:
            class_dict[arg] = asset_entry[arg]

    instance_kwargs = class_dict.copy()
    instance_kwargs.update(base_class_dict)

    # pass in the class args to the specific asset type class, kwargs go to BaseAsset class
    return asset_class(**instance_kwargs)


def get_asset_by_database_path(database_path):
    """
    Return the asset by using the database relative path
    :param database_path:
    :return:
    """


