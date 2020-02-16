class BaseAsset(object):
    def __init__(self, name, uid, upid, publish_time, project, shot, asset, version):
        self.__name = name
        self.__uid = uid
        self.__user_publish_id = upid
        self.__asset_publish_time = publish_time
        self.__project = project
        self.__shot = shot
        self.__asset = asset
        self.__version = version
        self.__asset_type = self

        # paths relative to OS
        self.__linux_path = str()
        self.__windows_path = str()

        # pat__hs generated from db manager config
        self.__asset_relative_tree_path = str()
        self.__asset_publish_path = str()

    def _generate_os_paths(self):
        # TODO add method/func in utils to generate linux and windows paths for asset
        return

    #  method we call in case we would need to cast this instance to another asset type
    def _set_asset_type(self):
        self.__asset_type = self

    def _set_publish_info(self, tree_path, publish_path):
        self.__asset_relative_tree_path = tree_path
        self.__asset_publish_path = publish_path

    def _get_asset_id(self):
        return self.__uid

    def _get_asset_version(self):
        return self.__version

    def _get_asset_published_user(self):
        return self.__user_publish_id

    def _get_asset_type(self):
        return type(self)

