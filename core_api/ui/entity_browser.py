import os
import sys
from Qt import QtWidgets, QtCompat
from bson import ObjectId

from core_api.managers.asset_manager import AssetReader
from core_api.assets.model_asset import ModelAsset
from core_api.assets.anim_asset import AnimAsset
from core_api.assets.scene_asset import SceneAsset
from core_api.assets.image_asset import ImageAsset
from core_api.assets.texture_asset import TextureAsset
from core_api.assets.fx_asset import FXAsset
from core_api.assets.rig_asset import RigAsset
from core_api.assets.lighting_asset import LightingAsset


from core_api.conf import ASSET_BIN, SHOTS
from core_api.utils import remove_namespaces

# these are the catgegories in the UI mapped to the asset type reps which get passed into query api
asset_categories = {
    "Model": ModelAsset,
    "Animation": AnimAsset,
    "Scene": SceneAsset,
    "Image": ImageAsset,
    "Texture": TextureAsset,
    "FX": FXAsset,
    "Rig": RigAsset,
    "Lighting": LightingAsset
}


class EntityBrowser(QtWidgets.QMainWindow):
    def __init__(self, ):
        self.ui = self.load_this_ui()
        self.show_gui()
        self.asset_reader = AssetReader()
        self.load_project_fields()
        self.setup_signals()
        self.project = str()
        self.asset = str()
        self.shot = str()
        self.found_assets = dict()

    def load_this_ui(self):
        return QtCompat.loadUi(str(__file__).replace('.py', '_ui.ui'))

    def show_gui(self):
        self.ui.show()

    def set_info(self):
        self.project = self.ui.comboBox_project.currentText()
        self.asset   = self.ui.comboBox_asset.currentText()
        self.shot    = self.ui.comboBox_shot.currentText()

    def load_project_fields(self):
        self.ui.comboBox_project.clear()
        for project in self.asset_reader.db_client.list_database_names():
            print project
            if 'users' not in project and 'admin' not in project:
                self.ui.comboBox_project.addItem(project)

    def populate_asset_dropdown(self):
        self.ui.comboBox_asset.clear()
        self.set_info()
        for asset in self.asset_reader.db_client[self.project][ASSET_BIN].find({}):
            self.ui.comboBox_asset.addItem(str(asset['name']))

    def populate_shot_dropdown(self):
        self.ui.comboBox_shot.clear()
        self.set_info()
        for shot in self.asset_reader.db_client[self.project][SHOTS].find({}):
            self.ui.comboBox_shot.addItem(str(shot['name']))

    def populate_entity_table(self):
        self.ui.tableWidget_found_assets.setColumnCount(0)
        self.ui.tableWidget_found_assets.setRowCount(0)
        found_assets = self.asset_reader.get_assets_by_project(asset_categories[self.ui.comboBox_asset_type.currentText()],
                                                               self.project, representations=True)
        if not found_assets:
            return

        columns_index_by_name = dict()
        columns_index_by_name_counter = 0

        index = 0
        # create the columns for the assets
        for k, v in remove_namespaces(found_assets[0].__dict__).iteritems():
            self.ui.tableWidget_found_assets.insertColumn(index)
            self.ui.tableWidget_found_assets.setHorizontalHeaderItem(index, QtWidgets.QTableWidgetItem(str(k)))
            if k not in columns_index_by_name.keys():
                columns_index_by_name[k] = columns_index_by_name_counter
                columns_index_by_name_counter += 1
            index += 1

        asset_index = 0
        property_index = 0
        for asset in found_assets:
            print "YPYP" , asset.get_asset_name()
            self.ui.tableWidget_found_assets.insertRow(asset_index)
            for k, v in remove_namespaces(asset.__dict__).iteritems():
                self.ui.tableWidget_found_assets.setItem(asset_index, columns_index_by_name[k],
                                                         QtWidgets.QTableWidgetItem(str(v)))
                property_index += 1
            asset_index += 1
            property_index = 0

    def setup_signals(self):
        for combo in [self.ui.comboBox_project.currentIndexChanged, self.ui.comboBox_asset.currentIndexChanged,
                      self.ui.comboBox_shot.currentIndexChanged, self.ui.comboBox_asset_type.currentIndexChanged]:
            combo.connect(self.populate_entity_table)
            combo.connect(self.set_info)
        self.ui.comboBox_project.currentIndexChanged.connect(self.populate_asset_dropdown)
        self.ui.comboBox_project.currentIndexChanged.connect(self.populate_entity_table)
        self.ui.comboBox_project.currentIndexChanged.connect(self.populate_shot_dropdown)
        self.ui.comboBox_asset.currentIndexChanged.connect(self.set_info)
        self.ui.comboBox_shot.currentIndexChanged.connect(self.set_info)

    def resize_table(self):
        pass


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    instance = EntityBrowser()
    app.exec_()
