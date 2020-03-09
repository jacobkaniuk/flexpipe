import unittest
from core_api.managers.asset_manager import AssetManager
from core_api.assets.image_asset import ImageAsset
from core_api.assets.texture_asset import TextureAsset
from core_api.assets.layout_asset import LayoutAsset
from core_api.assets.base_asset import BaseAsset
from core_api.production import remove_namespaces
from collections import OrderedDict


class AssetManagementTest(unittest.TestCase):
    def test_write_dummy_data(self, name='TEST_ASSET_A', created_by=22, publish_time='2020-6-3-22:21:25',
                              project='test_this_new_project', shot='TEST_SCENE', version=1,
                              asset_type='BaseAsset', **kwargs):
        asset_manager = AssetManager()
        entry = {
            'name': name,
            'created_by': created_by,
            'publish_time': publish_time,
            'project': project,
            'shot': shot,
            'version': version,
            'asset_type': asset_type,
        }
        for key, val in kwargs.items():
            entry[key] = val

        if not asset_manager.db_client[project]['published_assets'].find_one(entry):
            print "Did not find any entry with given attributes. Adding to collection."
            asset_manager.db_client[project]['published_assets'].insert_one(entry)

    def print_asset_info(self, asset):
        if isinstance(asset, list):
            for i in asset:
                i = remove_namespaces(i.__dict__)
                for key, val in i.items():
                    len_just = 30 - len(key)
                    print key, ": ".rjust(len_just), val
                print "\n"
        else:
            if isinstance(asset, dict):
                item = remove_namespaces(asset.__dict__)
                for key, val in item.items():
                    len_just = 30 - len(key)
                    print key, ": ".rjust(len_just), val
                print "\n"

    def test_get_published_asset(self):
        asset_manager = AssetManager()
        # asset_manager.get_published_asset()
        entry = OrderedDict(
            name='BALL_LARGE_A',
            created_by=22,
            publish_time='2020-6-3-22:21:25',
            project='test_this_new_project',
            shot='PLAYGROUND_ASSETS',
            version=1,
            asset_type='ImageAsset',
            colorspace='sRGB',
            resolution=[1920, 1080],
            bit_depth=8,
            data_space='int',
            image_format='Jpeg'
        )
        entry2 = OrderedDict(
            name='BALL_LARGE_A',
            created_by=22,
            publish_time='2020-6-3-22:21:25',
            project='test_this_new_project',
            shot='PLAYGROUND_ASSETS',
            version=2,
            asset_type='ImageAsset',
            colorspace='sRGB',
            resolution=[1920, 1080],
            bit_depth=8,
            data_space='int',
            image_format='Jpeg'
        )
        entry3 = OrderedDict (
            name='BALL_LARGE_A',
            created_by=22,
            publish_time='2020-6-3-22:21:25',
            project='test_this_new_project',
            shot='PLAYGROUND_ASSETS',
            version=3,
            asset_type='ImageAsset',
            colorspace='sRGB',
            resolution=[1920, 1080],
            bit_depth=8,
            data_space='int',
            image_format='Jpeg'
        )

        for item in [entry, entry2, entry3]:
            self.test_write_dummy_data(**item)

        uid_asset = asset_manager.get_published_asset(uid='5e640f85424c4a5ed6ec54d3')
        default_asset = asset_manager.get_published_asset(project='test_this_new_project', shot='PLAYGROUND_ASSETS',
                                                  asset_type='ImageAsset', asset_name='BALL_LARGE_A')
        asset = asset_manager.get_published_asset(project='test_this_new_project', shot='PLAYGROUND_ASSETS',
                                                   asset_type='ImageAsset', asset_name='BALL_LARGE_A', version=4)
        asset2 = asset_manager.get_published_asset(project='test_this_new_project', shot='PLAYGROUND_ASSETS',
                                                  asset_type='ImageAsset', asset_name='BALL_LARGE_A', version=2)
        asset3 = asset_manager.get_published_asset(project='test_this_new_project', shot='PLAYGROUND_ASSETS',
                                                   asset_type='ImageAsset', asset_name='BALL_LARGE_A', prev_versions=4)

        for item in [uid_asset, default_asset, asset, asset2, asset3]:
            self.print_asset_info(item)

    def test_get_assets_by_type(self):
        asset_manager = AssetManager()
        image_assets = asset_manager.get_assets_by_type('ImageAsset', 'test_this_new_project', 'PLAYGROUND_ASSETS')
        for item in [image_assets]:
            self.print_asset_info(item)

    def test_get_user_assets(self):
        asset_manager = AssetManager()
        user_assets_uid = asset_manager.get_user_assets(uid='5e640f85424c4a5ed6ec54d3')
        user_assets_user_id = asset_manager.get_user_assets(user_id=4223)
        user_assets_username = asset_manager.get_user_assets(username='jacob.kaniuk')

        if user_assets_uid:
            print "\nFound assets created by uid: \n", self.print_asset_info(user_assets_uid)

        if user_assets_user_id:
            print "\nFound assets created by uid: \n", self.print_asset_info(user_assets_user_id)

        if user_assets_username:
            print "\nFound assets created by uid: \n", self.print_asset_info(user_assets_username)
