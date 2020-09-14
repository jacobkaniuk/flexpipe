from collections import OrderedDict
import logging
from logging import Logger
import warnings
import os
import datetime
from collections import Iterable
from collections import Counter
from core_api.utils import remove_namespaces


from pymongo import MongoClient
from pymongo import bulk
from pymongo import InsertOne
from pymongo import ReplaceOne
from pymongo import UpdateOne, UpdateMany
from pymongo import DeleteOne, DeleteMany
from pymongo import mongo_client
from pymongo import collection
from pymongo import command_cursor
from pymongo import cursor
from bson import ObjectId
from pymongo import errors

from filesystem_manager import FileSystem

from core_api.assets.base_asset import BaseAsset
from core_api.assets.model_asset import ModelAsset
from core_api.assets.scene_asset import SceneAsset
from core_api.assets.layout_asset import LayoutAsset
from core_api.assets.image_asset import ImageAsset
from core_api.assets.texture_asset import TextureAsset
from core_api.conf import PUBLISHED_ASSETS, ASSET_STATUS, DATABASE_PREFIX_ADDRESS

logging.basicConfig()


# use these keys to instantiate an asset object based on their unique member names.
# When extending, make sure inheritance order is set left->right : child->parent
ASSET_CLASS_ATTRS = OrderedDict({
    'parent_scene': LayoutAsset,
    'uv_method': TextureAsset,
    'colorspace': ImageAsset,
    'dcc_type': SceneAsset,
    'polycount': ModelAsset,
    'asset_relative_db_path': BaseAsset,
})

# use these to determine which asset we need to instantiate based on their suffix
ASSET_TYPE_SUFFIXES = {
    'mdl': ModelAsset,
    'tex': TextureAsset,
    'img': ImageAsset,
    'scn': SceneAsset,
    # 'rig': RigAsset,
    # 'fx': FXAssets,
    # 'lgt': LightingAsset,
    # 'anim': AnimAsset,
    'lay': LayoutAsset
}


class AssetReader(object):
    def __init__(self):
        super(AssetReader, self).__init__()
        self.db_client = MongoClient('localhost')  # TODO pass db server we want to connect to

    def get_published_asset(self, uid=None, project=None, shot=None, asset_type=None,
                            asset_name=None, version=None, prev_versions=None, verbose=True):
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
                if database not in ['admin', 'config', 'users', 'local']:
                    if verbose:
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

        if issubclass(asset_type, BaseAsset):
            asset_type = asset_type.__name__

        query = ({'name': asset_name,
                  'project': project,
                  'shot': shot,
                  'asset_type': asset_type})

        # get back all the results, unfiltered
        results = self.db_client[project][PUBLISHED_ASSETS].find(query)
        result_count = self.db_client[project][PUBLISHED_ASSETS].count_documents(query)

        if verbose:
            if result_count < 1:
                print "Could not find any assets with the given fields: \n\n\t-{}\n\t-{}\n\t-{}\n\t-{}\n".format(
                    project, shot, asset_name, asset_type
                )
                return None

        # return a specific version from our arg
        if version:
            if not isinstance(version, int):
                raise TypeError("Could not make result version query. Wrong type provided. Expected: {}. Got: {}".format
                                (int, type(version)))

            if version > 0:
                # get the version based on the exact number that we pass in ie(version=3 will return version 3 if exist)
                for result in results:
                    if int(result['version']) == int(version):
                        return create_asset_representation(result)

            if version < 0:
                # get the version n versions away from latest version (ie. version=-2 will return second last result)
                versions = sorted(results, key=lambda x: int(x['version']))[version:]
                return create_asset_representation(versions[version:][0])  # pass result as dict not list

            if verbose:
                print "Did not find any asset with specified fields in results: Version {}".format(version)
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
        if verbose:
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
            if asset_type not in ASSET_CLASS_ATTRS.values():
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

    def get_assets(self, asset_type=None, project=None, shot=None, max_count=None,
                   dept=None, from_date=None, to_date=None, location=None, status=None, representations=False):

        # TODO see if we can refactor this method and get_published_assets above to be one general purpose method
        #  for all asset search/retrieval purposes

        """
        General purpose method to get all published assets from a project based on given "filters" (params)
        :param asset_type: str/BaseAsset type of assets we want to retrieve
        :param project: str name of project to search in
        :param shot: str name of shot we want to search in
        :param max_count: int limit our results length
        :param dept: str search by department/stage/type
        :param from_date: datetime/str starting date for date range search
        :param to_date: datetime/str ending date for date range search
        :param location: str search by location of published user
        :param status: int search by status of the asset
        :param representations: bool return results as flexpipe asset objects or as dicts from database results
        :return: list all found assets as dicts. can then be instantiated by feeding into get published asset method
        """
        if not asset_type:
            asset_type = {}

        if asset_type:
            if issubclass(asset_type, BaseAsset):
                asset_type = asset_type.__name__

        if project not in self.db_client.list_database_names():
            raise errors.CollectionInvalid("Could not find specified project in database: {}\n".format(project))

        query = dict()
        for key, value in {'asset_type': asset_type, 'project': project, 'shot': shot,
                           'department': dept, 'location': location, 'status': status}.items():
            if value:
                if value.__class__ not in [str, int, unicode]:
                    raise TypeError("Please provide a valid type to search db. "
                                    "Expected: {} Got: {}".format([str, int], type(value)))
                query.update({key: value})

        if from_date and to_date:
            query.update({'publish_time': {'$gte': from_date, '$lt': to_date}})

        if max_count:
            col_published_assets = self.db_client[project][PUBLISHED_ASSETS]
            # use this to limit how many assets we're going to get back
            if not isinstance(max_count, int):
                if not isinstance(max_count, long):
                    if not max_count >= 1:
                        raise TypeError("Please provide a valid numeric value for result length constraint.")

            # return the assets as python object representations
            if representations:
                results = [i for i in cursor.Cursor(col_published_assets, filter=query, limit=max_count)]
                return [create_asset_representation(i) for i in results]

            # return just the db cursor results
            return [i for i in cursor.Cursor(col_published_assets, filter=query, limit=max_count)]

        # no limit, return all found items
        if representations:
            results = [i for i in self.db_client[project][PUBLISHED_ASSETS].find(query)]
            return [create_asset_representation(i) for i in results]

        return [i for i in self.db_client[project][PUBLISHED_ASSETS].find(query)]

    def get_assets_by_project(self, asset_type, project, **kwargs):
        return self.get_assets(asset_type, project, **kwargs)

    def get_assets_by_shot(self, asset_type, project, shot, **kwargs):
        return self.get_assets(asset_type, project, shot, **kwargs)

    def get_asset_by_database_path(self, database_path):
        """
        Return the asset by using the database relative path (ie. project/cre_snake_a/mdl/2
        :param database_path:
        :return:
        """

        # TODO make sure to add check for suffix validating at end, value error thrown now

        argument_error_message = "Please provide required arguments: {}{}/{}/{}\n{}\nor\n{}".format(
            DATABASE_PREFIX_ADDRESS, 'project', 'shot', 'asset_name', 'version (optional),'
            'eg: flex://test_project/ENV_SHOPPING_CENTRE/PROP_SHOPPING_CART_A_mdl/4',
            ' as list: ["flex://", "test_project", "ENV_SHOPPING_CENTRE", "PROP_SHOPPING_CART_A", "mdl", "4"]')

        project     = None
        shot        = None
        asset_name  = None
        version     = None

        if isinstance(database_path, str):
            if not database_path.startswith(DATABASE_PREFIX_ADDRESS):
                raise RuntimeWarning("Please make sure you add correct address at start of provided. \nExpected: {} \n"
                                     "Got: {}\n".format(DATABASE_PREFIX_ADDRESS, database_path[:len(DATABASE_PREFIX_ADDRESS)]))

            database_path = database_path.rsplit(DATABASE_PREFIX_ADDRESS)[-1]
            database_path = database_path.rsplit(os.path.sep)

        elif isinstance(database_path, list):
            for item in database_path:
                if not isinstance(item, str):
                    raise TypeError("Please provided list of: {} to create query.".format(str))

        if not len(database_path) == 4:
            if not len(database_path) == 3:
                raise RuntimeError(argument_error_message)

        project     = database_path[0]
        shot        = database_path[1]
        asset_name  = database_path[2]

        if len(database_path) == 4:
            version     = database_path[3]

        if not all([project, shot, asset_name]) != '' or None:
            raise RuntimeError("One or more invalid argument values. {}".format(argument_error_message))

        asset_suffix = asset_name.rsplit('_', 1)[-1]
        split_asset_name = asset_name.rsplit('_', 1)[0]
        asset_type = ASSET_TYPE_SUFFIXES[asset_suffix]
        version = int(version) if version else None

        return self.get_published_asset(project=project, shot=shot, asset_type=asset_type,
                                        asset_name=split_asset_name, version=version)


class AssetOperations(object):
    class Insert:
        def __init__(self):
            pass

    class Update:
        def __init__(self):
            pass

    class Delete:
        def __init__(self):
            pass

    class Archive:
        def __init__(self):
            pass

    @staticmethod
    def unpack_asset_info(asset, **kwargs):
        if not isinstance(asset, BaseAsset):
            raise TypeError("Expected instance of {}. Got: {}.\n".format(BaseAsset, type(asset)))

        entry = {
            'name':         asset.get_asset_name(),
            'created_by':   asset.get_asset_published_user(),
            'publish_time': datetime.datetime.utcnow(),
            'project':      asset.get_asset_project(),
            'shot':         asset.get_asset_shot(),
            'version':      asset.get_asset_version(),
            'asset_type':   asset.get_asset_type(),
        }

        for key, val in kwargs.items():
            entry[key] = val

        return entry

    @staticmethod
    def add_asset_entry(asset, **kwargs):
        """
        Add a new asset entry to project in database
        :param asset: BaseAsset asset we want to add
        """
        return UpdateOne(AssetOperations.unpack_asset_info(asset, **kwargs),
                         {"$set": remove_namespaces(asset.__dict__)}, upsert=True)

    @staticmethod
    def update_asset_entry(asset, **kwargs):
        """
        Update an asset entry in our database
        :param asset: BaseAsset asset we want to update
        """
        from pymongo.bulk import BulkUpsertOperation
        return UpdateOne(asset, AssetOperations.unpack_asset_info(asset, **kwargs))

    @staticmethod
    def delete_asset_entry(asset, archive=False, **kwargs):
        """
        Delete an asset entry in our database
        :param asset: BaseAsset asset we want to delete from database
        :param archive: bool soft deletion of asset (move to archive database/location)
        """
        return DeleteOne(AssetOperations.unpack_asset_info(asset, **kwargs))

    @staticmethod
    def archive_asset_entry(asset, **kwargs):
        UpdateOne(asset, AssetOperations.unpack_asset_info(asset, **kwargs))
        DeleteOne(AssetOperations.unpack_asset_info(asset, **kwargs))


class AssetWriter(object):
    def __init__(self):
        super(AssetWriter, self).__init__()
        self.db_client = MongoClient('localhost')  # TODO pass db server we want to connect to

    @staticmethod
    def exec_asset_operation(writer, assets, asset_operation):

        project_assets = dict()
        filesystem_ops = list()

        # function pointers for different database operations
        db_ops = {
            AssetOperations.Insert:  AssetOperations.add_asset_entry,
            AssetOperations.Update:  AssetOperations.update_asset_entry,
            AssetOperations.Delete:  AssetOperations.delete_asset_entry,
            AssetOperations.Archive: AssetOperations.archive_asset_entry
        }

        # function pointers to different filesystem operations
        fs_ops = {
            AssetOperations.Insert: FileSystem.copy_file,
            AssetOperations.Update: FileSystem.copy_file,
            AssetOperations.Delete: FileSystem.delete_file,
            AssetOperations.Archive: FileSystem.delete_file
        }

        if not isinstance(assets, Iterable):
            if not isinstance(assets, BaseAsset):
                raise RuntimeError("Could not add assets to database. "
                                   "Please make sure you are passing an instance of BaseAsset.\n")
            assets = [assets]

        for asset in assets:
            # build a dict based on different projects
            if asset.get_asset_project() not in project_assets:
                project_assets[asset.get_asset_project()] = list()

            # add a bulk operation object to our projects asset list
            project_assets[asset.get_asset_project()].append(db_ops[asset_operation](asset))

            # TODO split this out into a publishing module
            # add a filesystem bulk operation to our list
            filesystem_ops.append(str(fs_ops[asset_operation].__name__) + '({})'.format(asset.generate_os_paths()))

        # for project, bulk_ops in project_assets.iteritems():
        #     writer.db_client[project][PUBLISHED_ASSETS].

        for project, bulk_ops in project_assets.iteritems():
            print project
            print "bulk ioops: ", bulk_ops
            writer.db_client[project][PUBLISHED_ASSETS].bulk_write(bulk_ops)

        for item in filesystem_ops:
            pass ; #exec item


def create_asset_representation(asset_entry):
    """
    Create a flexpipe asset object from the databse results (dicts)
    :param asset_entry: dict database result object to create a flexpipe asset object from
    :return: BaseAsset flexpipe asset object
    """
    from inspect import getargspec

    if not isinstance(asset_entry, dict):
        raise TypeError("Cannot parse asset entry, invalid type. Expected: {} Got: {}".format(
            dict, type(asset_entry)))

    if asset_entry is None:
        raise ValueError('Could not create asset representation. No valid data found for instantiation.')

    # use this dict to pass in the values for our BaseAsset class
    base_class_dict = OrderedDict(
        name=asset_entry['name'],
        uid=asset_entry.get('_id', None),
        upid=asset_entry['created_by'],
        asset_type=asset_entry['asset_type'],
        publish_time=asset_entry.get('publish_time', None),
        project=asset_entry['project'],
        shot=asset_entry['shot'],
        version=asset_entry['version']
    )

    # figure out which class we should instantiate if we a specific field in the asset entry
    asset_class = None
    for key in asset_entry:
        if key in ASSET_CLASS_ATTRS:
            asset_class = ASSET_CLASS_ATTRS.get(key)
            break

    if asset_class is None:
        return None

    # if asset_class is None:
    #     raise KeyError("Could not find asset type to instance from support classes. Please make sure "
    #                    "you are passing in the correct data. Aborting...\n")

    class_dict = OrderedDict()
    for arg in asset_entry:
        # if we find that this arg is found in the class constructor, add it to our dict
        if arg in getargspec(asset_class.__init__).args:
            class_dict[arg] = asset_entry[arg]

    instance_kwargs = class_dict.copy()
    instance_kwargs.update(base_class_dict)

    # pass in the class args to the specific asset type class, kwargs go to BaseAsset class
    return asset_class(**instance_kwargs)

