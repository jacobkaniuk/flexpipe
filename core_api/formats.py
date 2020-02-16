# from OpenImageIO import 
from abc import abstractmethod


class ImageFormat(object):
    def __repr__(self):
        # attrs = list()
        for key, val in self.__dict__.items():
            print str(key), ": ", str(val)
        # return str(attrs)

    def __init__(self):
        self._extension = str()
        self._description = str()
        self.__max_bit_depth = int()
        self.__bit_depth = int()
        self.__metadata = dict()
        self.__colorspace = str()  # replace with colorspace type later
        self.__data_space = None
        self._supported_types = [
            'Jpeg',
            'Png',
            'Targa',
            'Tiff',
            'Bmp',
            'Dng',
            'OpenExr'
        ]

    @property
    def colorspace(self):
        return self.__colorspace
    
    @colorspace.setter
    def colorspace(self, output_space):
        """
        Convert the image from our current color space to the 
        target color space
        :param output_space: target colorspace 
        :return: 
        """
        
        return

    @property
    def bit_depth(self):
        return self.__bit_depth

    @bit_depth.setter
    def bit_depth(self, bit_depth):
        """
        Change bit depth of image to specified type
        :param bit_depth: int 8bit, 16bit, 32bit
        :return:
        """
        self.__bit_depth = bit_depth
        return

    @property
    def data_space(self):
        return self.__data_space

    @data_space.setter
    def data_space(self, data_type):
        """
        Change the data type from current type to provided. Will the data
        be stored as integer type data or floating point data. Floating
        point data can only be stored with bit depth 16 and above
        :param data_type: int() or float()
        :return:
        """

        if self.__bit_depth in [10, 12, 14, 16, 32]:
            # TODO find image library for image manipulation and conversion
            self.__data_space = data_type
            return

    @property
    def supported_types(self):
        return self._supported_types


class Jpeg(ImageFormat):
    def __init__(self):
        super(Jpeg, self).__init__()
        self._extension = '.jpg'
        self.bit_depth = 8
        self.data_space = int


class Png(ImageFormat):
    def __init__(self):
        super(Png, self).__init__()
        self._extension = '.png'
        self.bit_depth = 8
        self.data_space = int


class Targa(ImageFormat):
    def __init__(self):
        super(Targa, self).__init__()
        self._extension = '.tga'
        self.bit_depth = 16
        self.data_space = float


class Tiff(ImageFormat):
    def __init__(self):
        super(Tiff, self).__init__()
        self._extension = '.tiff'
        self.bit_depth = 16
        self.data_space = float


class Dng(ImageFormat):
    def __init__(self):
        super(Dng, self).__init__()
        self._extension = '.dng'
        self.bit_depth = 14
        self.data_space = float


class Bmp(ImageFormat):
    def __init__(self):
        super(Bmp, self).__init__()
        self._extension = '.bmp'
        self.bit_depth = 8
        self.data_space = int
