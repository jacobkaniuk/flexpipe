from core_api.assets.BaseAsset import BaseAsset


class SceneAsset(BaseAsset, parent=BaseAsset):
    def __init__(self, name, uid, upid, publish_time,
                       project, shot, asset, version):
        super(SceneAsset, self).__init__(name, uid, upid, publish_time,
                                         project, shot, asset, version)
        self.dcc_type = str()
        self.referenced_files = list()
        self.reference_count = len(self.referenced_files)
        self.is_reference = bool()

    def load_asset(self, dcc_handler):
        return dcc_handler.load_file(self.asset_publish_path)

