from core_api.assets.base_asset import BaseAsset


class LayoutAsset(BaseAsset):
    def __init__(self, **kwargs):
        super(LayoutAsset, self).__init__(self, **kwargs)
        self.__parent_scene = None
