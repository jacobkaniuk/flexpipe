import os
import sys
import datetime

from managers import asset_manager
from conf import PUBLISHED_ASSETS, SETTINGS, SHOTS, DEPARTMENTS


def remove_namespaces(item):
    if not isinstance(item, dict):
        raise TypeError("Could not remove namespaces from item(s). Expecting type: {} Got: {}".format(
            dict, type(item)))

    no_namespace_dict = dict()
    for key, value in item.items():
        key = str(key).rsplit('__')[-1]
        no_namespace_dict[key] = value
    return no_namespace_dict


def check_reader(instance):
    if instance.asset_reader is None:
        raise RuntimeError("Could not find asset manager instance. Please use init_manager method to create "
                           "instance first.")
    return True


class Project(object):
    def __init__(self, name, data_path=None, max_users=50):
        self.__name = name
        self.__data_path = data_path  # root prefix for where project will be stored
        self.__max_active_users = max_users
        self.__users = list()
        self.__resolution_x = int()
        self.__resolution_y = int()
        self.__default_dccs = dict()
        self.__shot_list = list()
        self.asset_reader = None

    def __repr__(self):
        return self.__name

    @property
    def name(self):
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
            print "Please pass an appropriate type (int)"
        try:
            self.__resolution_y = int(res[1])
        except TypeError:
            print "Please pass an appropriate type (int)"

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

    def number_of_shots(self):
        return len(self.__shot_list)

    # manager interface
    def init_asset_manager(self):
        self.asset_reader = asset_manager.AssetReader()

    def get_project_assets(self, *args, **kwargs):
        if check_reader(self):
            return self.asset_reader.get_assets_by_project(*args, project=self.__name, **kwargs)

    def get_assets_by_dept(self, dept, *args, **kwargs):
        """
        Get all the projects assets by department
        :param dept: str department we want to search
        :return:
        """
        if check_reader(self):
            if dept not in DEPARTMENTS.keys():
                if dept not in DEPARTMENTS.values():
                    raise KeyError("Invalid department code provided, not found in config. Please check config "
                                   "for valid departments")

            return self.asset_reader.get_assets(*args, project=self.__name, dept=dept, **kwargs)

    def get_assets_by_date(self, from_date=None, to_date=None, *args, **kwargs):
        """
        Get all projects assets using a date/time range. If no date range is provided through args,
        we return all assets published from beginning of the day
        :param from_date: datetime/str start date of range
        :param to_date: datetime/str end date of range
        :return:
        """
        # TODO assert dates are provided in ISO 8601 before we do a check on the db

        if check_reader(self):
            now = datetime.datetime.now().isoformat()
            day_begin = now.rsplit(':')[0] + ':00:00.000000'

            if not from_date and not to_date:
                return self.asset_reader.get_assets(*args, project=self.__name,
                                                    from_date=day_begin, to_date=now, **kwargs)

            elif from_date and to_date:
                return self.asset_reader.get_assets(*args, project=self.__name,
                                                    from_date=from_date, to_date=to_date, **kwargs)


class Shot(object):
    def __init__(self, project, name, start_frame=1, end_frame=50, users=None, fps=24):
        self.__project = project
        self.__name = name
        self.__start_frame = start_frame
        self.__end_frame = end_frame
        self.__users = users
        self.__frame_count = self.__end_frame - self.__start_frame
        self.__lut = str()
        self.__fps = fps
        self.asset_reader = None

    @property
    def project(self):
        return self.__project

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        return

    @property
    def duration(self):
        return "Duration: {sec} sec {frame} frames. Fps: {fps}".format(
            sec=int(self.frame_count / self.__fps),  # cast as int in case of python3+ later
            frame=self.frame_count % self.__fps,
            fps=self.__fps
        )

    def __update_frame_count(self):
        self.__frame_count = self.__end_frame - self.__start_frame

    @property
    def frame_count(self):
        return self.__frame_count

    @frame_count.setter
    def frame_count(self, count):
        """
        set the frame "range" for the shot. when value changed, start
        frame stays the same and end frame changes to match new offset
        :param count: int duration of shot. will be appended from start frame
        :return:
        """
        self.__end_frame = self.__start_frame + count
        self.__update_frame_count()

    def set_frame_range(self, start, end):
        self.__start_frame = start
        self.__end_frame = end
        self.__update_frame_count()

    @property
    def frame_range(self):
        return self.__start_frame, self.__end_frame

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

    def init_manager(self):
        self.asset_reader = asset_manager.AssetReader()

    def get_shot_assets(self, *args, **kwargs):
        if check_reader(self):
            return self.asset_reader.get_assets_by_shot(*args, shot=self.__name, project=self.project, **kwargs)

    def get_assets_by_dept(self, dept, *args, **kwargs):
        """
        Get all the projects assets by department
        :param dept: str department we want to search
        :return:
        """
        if check_reader(self):
            if dept not in DEPARTMENTS.keys():
                if dept not in DEPARTMENTS.values():
                    raise KeyError("Invalid department code provided, not found in config. Please check config "
                                   "for valid departments")

            return self.asset_reader.get_assets(*args, shot=self.__name, project=self.project, dept=dept, **kwargs)

    def get_assets_by_date(self, from_date=None, to_date=None, *args, **kwargs):
        """
        Get all projects assets using a date/time range. If no date range is provided through args,
        we return all assets published from beginning of the day
        :param from_date: datetime/str start date of range
        :param to_date: datetime/str end date of range
        :return:
        """
        if check_reader(self):
            now = datetime.datetime.now().isoformat()
            day_begin = now.rsplit(':')[0] + ':00:00.000000'

            if not from_date and not to_date:
                return self.asset_reader.get_assets(*args, shot=self.__name, project=self.project,
                                                    from_date=day_begin, to_date=now, **kwargs)

            elif from_date and to_date:
                return self.asset_reader.get_assets(*args, shot=self.__name, project=self.project,
                                                    from_date=from_date, to_date=to_date, **kwargs)
