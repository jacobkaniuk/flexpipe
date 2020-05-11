import core_api.production
from core_api.conf import ASSET_TYPE_SUFFIXES, ASSET_PREFIX_TYPES
from core_api.utils import generate_relative_path


class BaseAsset(object):
    def __init__(self, name=None, uid=None, asset_type=None, upid=None,
                 publish_time=None, project=None, shot=None, version=None, department=None, location=None):
        self.__name = name
        self.__uid = uid
        self.__asset_type = asset_type
        self.__user_publish_id = upid
        self.__asset_publish_time = publish_time
        self.__project = project
        self.__shot = shot
        self.__version = version
        self.__department = department
        self.__publish_location = location

        # paths relative to OS
        self.__linux_path = str()
        self.__windows_path = str()

        # paths generated from db manager config
        self.__asset_relative_db_path = generate_relative_path(self)
        self.__asset_publish_path = None

    def __repr__(self):
        return "<{} at {}. Project: {}, Shot: {}>".format(
            self.__class__.__name__, hex(id(self)), self.__project, self.__shot)

    def get_asset_info(self):
        no_ns = core_api.production.remove_namespaces(self.__dict__)
        longest_attr = max(no_ns.keys(), key=len)
        print self.__repr__()
        for key, value in no_ns.items():
            print "{}: {}".format(key.rjust(len(longest_attr)), value)
        print "\n"

    def generate_os_paths(self):
        # TODO add method/func in utils to generate linux and windows paths for asset
        return

    #  method we call in case we would need to cast this instance to another asset type
    def set_asset_type(self):
        self.__asset_type = self

    def set_publish_info(self, tree_path, publish_path):
        self.__asset_relative_db_path = tree_path
        self.__asset_publish_path = publish_path

    def get_asset_id(self):
        return self.__uid

    def get_asset_version(self):
        return self.__version

    def get_asset_published_user(self):
        return self.__user_publish_id

    def get_asset_type(self):
        return type(self)

    def get_asset_name(self):
        return self.__name

    def get_asset_project(self):
        return self.__project

    def get_asset_shot(self):
        return self.__shot

    def get_db_path(self):
        return self.__asset_relative_db_path

    def get_asset_type_suffix(self):
        for key, value in ASSET_TYPE_SUFFIXES.items():
            if str(self.__asset_type) == value:
                return key

    def get_asset_department(self):
        return self.__department

    def get_asset_publish_location(self):
        return self.__publish_location