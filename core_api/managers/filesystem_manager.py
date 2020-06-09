import os
import sys
import shutil


def check_file(path):
    return os.path.exists(path)


def check_isdir(path):
    return os.path.isdir(path)


class FileSystem(object):
    platform = sys.platform

    def __init__(self):
        pass

    @staticmethod
    def move_file(src, dst):
        """
        Move a file from source to destination location
        :param src: str source path
        :param dst: str destination path
        :return:
        """
        if all([check_file(src), check_file(dst)]):
            try:
                shutil.move(src, dst)
            except OSError as e:
                print "Could not move file: {src} to destination: {dst}. Error: {err}".format(src=src, dst=dst, err=e)

    @staticmethod
    def copy_file(src, dst, sym_links=True):
        """
        Copy a file from source to destination location
        :param src: str source path
        :param dst: str destination path
        :param sym_links: bool copy symlinks
        :return:
        """
        if all([check_file(src), check_file(dst)]):
            try:
                shutil.copy2(src, dst, follow_symlinks=sym_links)
            except OSError as e:
                print "Could not copy file: {src} to destination: {dst}. Error: {err}".format(src=src, dst=dst, err=e)

    @staticmethod
    def delete_file(src, dst=None, archive=False):
        if check_file(src):
            try:
                if archive:
                    if check_isdir(dst):
                        shutil.copy2(src, dst)
                os.remove(src)
            except OSError as e:
                print "Could not copy file: {src} to destination: {dst}. Error: {err}".format(src=src, dst=dst, err=e)

