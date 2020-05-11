import os
from conf import get_database_prefix_address


def generate_relative_path(asset):
    # will return a relative db path for the asset ie. flex:\\test_project\ENV_TEST\PROP_HAMMER_A\model\4
    # print [get_database_prefix_address(), asset.get_asset_project(),
    #        asset.get_asset_shot(), asset.get_asset_name(), asset.get_asset_type_suffix(), asset.get_asset_version()]
    #
    # return "Test"
    return "{}{}{sep}{}{sep}{}{sep}{}".format(get_database_prefix_address(), asset.get_asset_project(), asset.get_asset_shot(),
                                  asset.get_asset_name() + '_' + asset.get_asset_type_suffix(),
                                              asset.get_asset_version(), sep=os.path.sep)
