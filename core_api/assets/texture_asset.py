from core_api.assets.base_asset import BaseAsset
from core_api.assets.image_asset import ImageAsset


class TextureAsset(ImageAsset, BaseAsset):
    def __init__(self, **kwargs):
        super(TextureAsset, self).__init__(**kwargs)

