import unittest
from core_api.managers import ProductionManager


class ProjectManipulationTest(unittest.TestCase):
    def test_database_connection(self):
        # test if we can establish a connection with the database
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        return mongodb_client.connect_to_database('localhost')

    def test_project_addition(self):
        # test if we can add a project to the databsase
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        project = mongodb_client.create_project(int(23445))
        # project = mongodb_client.create_project('new_unittest_project')

    def test_project_deletion(self):
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        project = mongodb_client.create_project('new_unittest_project')
        mongodb_client.database_connection.drop_database(project)