from core_api.assets.base_asset import BaseAsset


class SceneAsset(BaseAsset):
    def __init__(self, dcc_type=None, referenced_files=None, **kwargs):
        super(SceneAsset, self).__init__(**kwargs)
        self.__dcc_type = dcc_type
        self.__referenced_files = referenced_files

    def load_scene(self, dcc_handler):
        return dcc_handler.load_file(self.__asset_publish_path)
