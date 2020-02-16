import BaseAsset
from colour.io import image


class ImageAsset(BaseAsset):
    def __init__(self):
        self.image_path = str()
        self.colorspace = str()
        self.resolution = tuple()
        self.bit_depth = int()
        #self.image_format = ImageFormat()