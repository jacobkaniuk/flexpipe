import unittest
from core_api.managers import production_manager
from core_api import production
from core_api.conf import ASSET_BIN, PUBLISHED_ASSETS

class ProjectManipulationTest(unittest.TestCase):
    def test_db_client(self):
        # test if we can establish a connection with the database
        prod_manager = production_manager.ProductionManager('mongodb')
        return prod_manager.connect_to_database('localhost')

    def test_project_addition(self):
        # test if we can add a project to the databsase
        prod_manager = production_manager.ProductionManager('mongodb')
        new_project = production.Project('test_this_new_project', '/mnt/VFX/work', max_users=15)
        newer_project = production.Project('new_project', '/mnt/s/stuff/', max_users=50)

        print prod_manager.create_project(new_project)
        print prod_manager.create_project(newer_project)
        self.assertRaises(TypeError, prod_manager.create_project, 'testingin')
        self.assertRaises(TypeError, prod_manager.create_project, 155)
        self.assertRaises(TypeError, prod_manager.create_project, None)

    def test_project_update(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        new_project = production.Project(
            'test_this_new_project',
            '/mnt/VFX/works/doesthiswork',
            max_users=150
        )
        prod_manager.update_project(new_project)
        prod_manager.set_project_path(new_project.name, '/mnt/VFX/works/new_project_ath')

    def test_shot_addition(self, shot_name='ABC123'):
        prod_manager = production_manager.ProductionManager('mongodb')
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
        new_shot_c = production.Shot(
            new_project.name,
            'FZJ025',
            start_frame=1,
            end_frame=92,
            users=['jacob.kaniuk']
        )
        prod_manager.create_shot(new_project.name, new_shot)
        prod_manager.create_shot(new_project.name, new_shot_b)
        prod_manager.create_shot(new_project.name, new_shot_c, permission=4)
        prod_manager.update_shot(new_project.name, new_shot_c, permission=None)

    def test_shot_deletion(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        prod_manager.remove_shot('test_this_new_project', 'F11024')
        prod_manager.remove_shot('test_this_new_project', shot_id='5e4b8869c7a6ce3288e1847b')
        prod_manager.remove_shot(shot_id='5e4c92b7c7a6ce3288e18809')

    def test_project_info(self, project_name=None):
        prod_manager = production_manager.ProductionManager('mongodb')
        info = prod_manager.get_project_info('test_this_new_project')
        print "\nPROJECT INFO", info

    def test_project_deletion(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        new_project = production.Project(
            'delete_me_test_project',
            '/mnt/VFX/delete_me',
            max_users=15
        )
        prod_manager.create_project(new_project)
        prod_manager.db_client.drop_database(new_project.name)

    def test_asset_addition(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        new_project = production.Project(
            'test_this_new_project',
            '/mnt/VFX/work',
            max_users=225
        )
        prod_manager.create_asset(new_project, 'F11024', 'VHCL_GO_KART')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_TELESCOPE')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_BICYCLE')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_SLED')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_SOFA')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_TELEVISION')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_HAIR_DRYER')
        prod_manager.create_asset(new_project, 'F11024', 'PROP_HAMMER', max_weight='2Kg')
        prod_manager.update_asset('test_this_new_project', 'F11024', 'PROP_TELESCOPE', max_size=8001)
        prod_manager.update_asset('test_this_new_project', 'F11024', 'VHCL_GO_KART', validators=['validate.py', 'validateme.py'])
        prod_manager.update_asset(project_name='test_this_new_project', asset_id='5e4b7fbbe82acf15b012bf5d', max_size='22GB')
        prod_manager.update_asset(asset_id='5e4b88ecc7a6ce3288e184cc', food='GOOOD')

    def test_asset_deletion(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        prod_manager.remove_asset('test_this_new_project', asset_id='5e4c8905c7a6ce3288e186f1')
        # production_manager.remove_asset('test_this_new_project', 'F11024', 'PROP_TELESCOPE')
        prod_manager.remove_asset(asset_id='5e4e93bbc7a6ce3288e18abb')

    def test_get_assets_by_status(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        stuff = prod_manager.get_assets_by_status(1, project_name='test_this_new_project')
        for item in stuff:
            print item

    def test_get_assets_by_general(self):
        prod_manager = production_manager.ProductionManager('mongodb')
        print prod_manager.get_assets_by(project='test_this_new_project', shot='F11024')
        print prod_manager.get_assets_by(project='test_this_new_project', name='PROP_SOFA')
        print prod_manager.get_assets_by(project='test_this_new_project', size='40GB')

    def test_add_user(self):
        pass

    def test_get_user(self):
        from bson import ObjectId
        prod_manager = production_manager.ProductionManager('mongodb')
        id = ObjectId('5e4e93bbc7a6ce4178e18abb')
        result = prod_manager.db_client['test_this_new_project'][ASSET_BIN].find_one({'_id': id})
        print result

    def test_get_project_assets(self):
        proj = production.Project('test_this_new_project')
        proj.init_asset_manager()
        for i in proj.get_project_assets('ImageAsset'):
            print i['asset_type'], i
        for i in proj.get_project_assets('BaseAsset'):
            print i['asset_type'], i
        for i in proj.get_project_assets(asset_type='BaseAsset', max_count=2):
            print "limited: ", i['asset_type'], i
        for i in proj.get_project_assets(asset_type='ImageAsset', max_count=6, representations=True):
            i.get_asset_info()

    def test_get_shot_assets(self):
        shot = production.Shot('test_this_new_project', 'PLAYGROUND_ASSETS')
        shot.init_asset_manager()
        for i in shot.get_shot_assets(asset_type='ImageAsset'):
            print i

    def test_get_assets_by_date(self):
        import datetime
        proj = production.Project('test_this_new_project')
        shot = production.Shot('test_this_new_project', 'PLAYGROUND_ASSETS')

        proj.init_asset_manager()
        shot.init_asset_manager()

        _from = datetime.datetime(2020, 1, 1, 1, 0, 0)
        _to   = datetime.datetime(2020, 12, 30, 11, 59, 59)

        for i in proj.get_assets_by_date(_from, _to):
            print "By dates: ",  i

        for i in shot.get_assets_by_date(_from, _to):
            print "By dates: ", i


    def test_get_assets_by_dept(self):
        proj = production.Project('test_this_new_project')
        shot = production.Shot('test_this_new_project', 'PLAYGROUND_ASSETS')

        proj.init_asset_manager()
        shot.init_asset_manager()

        for i in proj.get_assets_by_dept('MDL'):
            print "Dept asset: ", i

        for i in shot.get_assets_by_dept('MDL'):
            print "Dept asset: ", i


    def test_get_assets_by_location(self):
        proj = production.Project('test_this_new_project')
        proj.init_asset_manager()
        for i in proj.get_assets_by_location('toronto', representations=True):
            print i.get_asset_info()

