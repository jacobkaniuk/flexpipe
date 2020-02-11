class BaseAsset(object):
    def __init__(self, name, uid, upid, publish_time, project, shot, asset, version):
        self.name = name
        self.uid = uid
        self.user_publish_id = upid
        self.asset_publish_time = publish_time
        self.project = project
        self.shot = shot
        self.asset = asset
        self.version = version
        self.asset_type = self

        # paths relative to OS
        self.linux_path = str()
        self.windows_path = str()

        # paths generated from db manager config
        self.asset_relative_tree_path = str()
        self.asset_publish_path = str()

    def _generate_os_paths(self):
        # TODO add method/func in utils to generate linux and windows paths for asset
        return

    #  method we call in case we would need to cast this instance to another asset type
    def _set_asset_type(self):
        self.asset_type = self

    def _set_publish_info(self, tree_path, publish_path):
        self.asset_relative_tree_path = tree_path
        self.asset_publish_path = publish_path

    def _get_asset_id(self):
        return self.uid

    def _get_asset_version(self):
        return self.version

    def _get_asset_published_user(self):
        return self.user_publish_id

    def _get_asset_type(self):
        return type(self)

