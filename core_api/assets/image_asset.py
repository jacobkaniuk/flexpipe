from base_asset import BaseAsset
from colour.io import image
from core_api.formats import ImageFormat


class ImageAsset(BaseAsset):
    def __init__(self, colorspace=None, resolution=None, bit_depth=None,
                 data_space=None, image_format=None, **kwargs):
        super(ImageAsset, self).__init__(**kwargs)
        self.__colorspace = colorspace
        self.__resolution = resolution
        self.__bit_depth = bit_depth
        self.__data_space = data_space
        self.__image_format = image_format
