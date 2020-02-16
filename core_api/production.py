import os
import sys


class Project(object):
    def __init__(self):
        self.__name = str()
        self.__data_path = str()
        self.__resolution_x = int()
        self.__resolution_y = int()
        self.__default_dccs = dict()
        self.__max_active_users = int()
        self.hierarchy = dict()

    def __repr__(self):
        return self.__name

    @property
    def data_path(self):
        return self.__data_path

    @data_path.setter
    def data_path(self, data_path):
        self.__data_path = data_path

    @property
    def resolution(self):
        return [self.__resolution_x, self.__resolution_y]

    @resolution.setter
    def resolution(self, res):
        """
        Set the default resolution for the project. All shots without
        overridden res will use this res.
        :param res: list/tuple x and y resolution as int
        :return:
        """
        try:
            self.__resolution_x = int(res[0])
        except TypeError:
            print"Please pass an appropriate type (int)"
        try:
            self.__resolution_y = int(res[1])
        except TypeError:
            print"Please pass an appropriate type (int)"

    @property
    def max_active_users(self):
        """
        :return: int the max number of users allowed on this project
        """
        return self.__max_active_users

    @max_active_users.setter
    def max_active_users(self, max_users):
        """
        Set max number of users for project
        :param max_users: int max user count
        :return:
        """
        self.__max_active_users = max_users

    def get_number_of_shots(self):
        return len()


class Shot(object):
    def __init__(self, project, name, start_frame, end_frame):
        self.__project = project
        self.__name = name
        self.__start_frame = start_frame
        self.__end_frame = end_frame
        self.__frame_range = self.__end_frame - self.__start_frame
        self.__num_published_assets = int()
        self.__lut = str()

    @property
    def frame_count(self):
        return self.__frame_range

    @frame_count.setter
    def frame_count(self, range):
        """
        set the frame "range" for the shot. when value changed, start
        frame stays the same and end frame changes to match new offset
        :param count: list/tuple start and end frame of the shot
        :return:
        """
        self.__start_frame = int(range[0])
        self.__end_frame = int(range[1])
        self.__frame_range = self.__end_frame - self.__start_frame

    def __repr__(self):
        return self.__name

    def __gt__(self, other):
        return max(self.__frame_count,
                   other.frame_count)

    def __lt__(self, other):
        return min(self.__frame_count,
                   other.frame_count)

    def __eq__(self, other):
        return self.__frame_count == other.frame_count