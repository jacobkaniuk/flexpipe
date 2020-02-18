import unittest
from core_api.managers import ProductionManager
from core_api import production


class ProjectManipulationTest(unittest.TestCase):
    def test_database_connection(self):
        # test if we can establish a connection with the database
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        return mongodb_client.connect_to_database('localhost')

    def test_project_addition(self):
        # test if we can add a project to the databsase
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        new_project = production.Project(
           'test_this_new_project',
           '/mnt/VFX/work',
           max_users=15
        )
        print mongodb_client.create_project(new_project)
        self.assertRaises(TypeError, mongodb_client.create_project, 'testingin')
        self.assertRaises(TypeError, mongodb_client.create_project, 155)
        self.assertRaises(TypeError, mongodb_client.create_project, None)


    def test_project_update(self):
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        new_project = production.Project(
            'test_this_new_project',
            '/mnt/VFX/works/doesthiswork',
            max_users=150
        )
        mongodb_client.update_project(new_project)
        mongodb_client.set_project_path(new_project.name, '/mnt/VFX/works/new_project_ath')


    def test_shot_addition(self, shot_name='ABC123'):
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        new_project = production.Project(
            'test_this_new_project',
            '/mnt/VFX/work',
            max_users=225
        )
        new_shot = production.Shot(
            new_project.name,
            'F11024',
            start_frame=1,
            end_frame=216,
            users=['jacob.kaniuk']
        )
        new_shot_b = production.Shot(
            new_project.name,
            'FZ3025',
            start_frame=1,
            end_frame=92,
            users=['jacob.kaniuk']
        )
        mongodb_client.create_shot(new_project.name, new_shot)
        mongodb_client.create_shot(new_project.name, new_shot_b)

    def test_project_info(self, project_name=None):
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        info = mongodb_client.get_project_info('test_this_new_project')
        print "\nPROJECT INFO", info

    def test_project_deletion(self):
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        new_project = production.Project(
            'delete_me_test_project',
            '/mnt/VFX/delete_me',
            max_users=15
        )
        mongodb_client.create_project(new_project)
        mongodb_client.database_connection.drop_database(new_project.name)

    def test_asset_addition(self):
        mongodb_client = ProductionManager.ProductionManager('mongodb')
        new_project = production.Project(
            'test_this_new_project',
            '/mnt/VFX/work',
            max_users=225
        )
        mongodb_client.create_asset(new_project, 'F11024', 'VHCL_GO_KART')
        mongodb_client.create_asset(new_project, 'F11024', 'PROP_TELESCOPE')
        mongodb_client.update_asset('test_this_new_project', 'F11024', 'PROP_TELESCOPE', max_size=39)
        mongodb_client.update_asset('test_this_new_project', 'F11024', 'VHCL_GO_KART', validators=['validate.py', 'validateme.py'])
        mongodb_client.update_asset(project_name='test_this_new_project', asset_id='5e4b7fbbe82acf15b012bf5d', max_size='22GB')
