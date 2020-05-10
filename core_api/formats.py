# from imageio import formats


class ImageFormat(object):
    def __repr__(self):
        # attrs = list()
        for key, val in self.__dict__.items():
            print str(key), ": ", str(val)
        # return str(attrs)

    def __init__(self, ext, bit_depth, data_space):
        self._extension = ext
        self._description = str()
        self.__max_bit_depth = int()
        self.__bit_depth = bit_depth
        self.__metadata = dict()
        self.__colorspace = None  # replace with colorspace type later
        self.__data_space = data_space
        self.types = [
            'Jpeg',
            'Png',
            'Targa',
            'Tiff',
            'Bmp',
            'Dng',
            'OpenExr'
        ]

    def change_format(self, target_format):
        # TODO add method to easily change between image formats to avoid making
        #  always needing to make calls to library. Maybe move this out as a
        #  utility function to the module instead, we'll see
        return

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
            #  preferebly oiio and ocio for image/color, quite a few depends though
            self.__data_space = data_type
            return

    @property
    def supported_types(self):
        return self.supported_types


class Jpeg(ImageFormat):
    def __init__(self):
        super(Jpeg, self).__init__('.jpg', 8, int)
    # add format specific functionality here


class Png(ImageFormat):
    def __init__(self):
        super(Png, self).__init__('.png', 8, int)
    # add format specific functionality here maybe


class Targa(ImageFormat):
    def __init__(self):
        super(Targa, self).__init__('.tga', 16, float)
    # add format specific functionality here


class Tiff(ImageFormat):
    def __init__(self):
        super(Tiff, self).__init__('.tiff', 16, float)
    # add format specific functionality here


class Dng(ImageFormat):
    def __init__(self):
        super(Dng, self).__init__('.dng', 14, float)
    # add format specific functionality here


class Bmp(ImageFormat):
    def __init__(self):
        super(Bmp, self).__init__('.bmp', 8, float)
    # add format specific functionality here


IMAGE_FORMATS = {
    Jpeg: ['jpeg, JPEG, jpg, .jpeg, .jpg'],
    Png: ['png', 'PNG', '.png'],
    Targa: ['targa', '.tga', 'TARGA', 'TGA'],
    Tiff: ['tiff', 'TIFF', 'tif', 'TIF', '.tif', '.tiff'],
    Dng: ['dng', 'DNG', '.dng']
}


class Bundle(object):
    def __init__(self, items):
        from collections import Iterable
        super(Bundle, self).__init__()
        if not isinstance(items, Iterable):
            raise RuntimeError("Cannot create {} instance. "
                               "Items passed in not iterable.".format(self.__class__.__name__))
        self.__items = items


class Sequence(object):
    def __init__(self, frames, start_frame=None, end_frame=None):
        super(Sequence, self).__init__()
        for frame in frames:
            if not isinstance(frame, str):
                if not isinstance(frame, ImageFormat):
                    raise RuntimeError("Invalid type passed to Sequence instance. Expected "
                                       "{} or {}, got: {}".format(str.__name__,
                                                                  ImageFormat.__name__,
                                                                  type(frame)))

        self.start_frame = int()
        self.end_frame = int()
        if start_frame and end_frame:
            self.start_frame, self.end_frame = start_frame, end_frame
        self.all_frames = list()
        self._get_sequence_info()

    def __lt__(self, other):
        return len(self.all_frames) < other.all_frames

    def __gt__(self, other):
        return len(self.all_frames) > other.all_frames

    def __eq__(self, other):
        return len(self.all_frames) == other.all_frames

    def __repr__(self):
        return "{} instance at {}. \nStart frame: {}, End Frame: {}, Total Frames: {}".format(
            self.__class__.__name__, hex(id(self)), self.start_frame, self.end_frame, len(self.all_frames)
        )

    def find_frame_pattern(self):
        # TODO maybe use regex to determine what the frame range/all frames are. we want to be able to
        #  support %01d, %02d, %03d and %04d frame numbering
        all_frames_dict = dict()
        for frame in self.all_frames:
            pass

        return all_frames_dict

    def _get_sequence_info(self):

        frames = self.find_frame_pattern()
        #
        # self.start_frame = min(sorted(frames['frame']))
        # self.end_frame   = max(sorted(frames['frame']))
