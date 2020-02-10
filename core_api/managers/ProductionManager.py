import os
import sys
from json import JSONDecoder


class ProductionManager(object, parent=None):
    def __init__(self, config_file):
        super(ProductionManager, self).__init__(self)
        self.config_file = config_file

    def parse_config(self):
        """
        Parse the config file and set contents to manager instance
        :return: bool did the contents get parsed properly
        """

    def connect_to_database(self, database_url):
        """
        Connect to the database given
        :param database_url: str
        :return:
        """
        return
