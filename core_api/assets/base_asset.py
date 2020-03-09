class BaseAsset(object):
    def __init__(self, name=None, uid=None, asset_type=None, upid=None,
                 publish_time=None, project=None, shot=None, version=None):
        self.__name = name
        self.__uid = uid
        self.__asset_type = asset_type
        self.__user_publish_id = upid
        self.__asset_publish_time = publish_time
        self.__project = project
        self.__shot = shot
        self.__version = version

        # paths relative to OS
        self.__linux_path = str()
        self.__windows_path = str()

        # paths generated from db manager config
        self.__asset_relative_tree_path = None
        self.__asset_publish_path = None

    def generate_os_paths(self):
        # TODO add method/func in utils to generate linux and windows paths for asset
        return

    #  method we call in case we would need to cast this instance to another asset type
    def set_asset_type(self):
        self.__asset_type = self

    def set_publish_info(self, tree_path, publish_path):
        self.__asset_relative_tree_path = tree_path
        self.__asset_publish_path = publish_path

    def get_asset_id(self):
        return self.__uid

    def get_asset_version(self):
        return self.__version

    def get_asset_published_user(self):
        return self.__user_publish_id

    def get_asset_type(self):
        return type(self)

