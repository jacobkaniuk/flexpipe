import os
import sys

import Qt
from Qt import QtWidgets, QtCore, QtGui



class BaseView(QtWidgets.QGraphicsView):
    def __init__(self, graphics_scene ):
        super(MyView, self).__init__()
        self.ui = None
        self.show_gui()
        self.setScene(graphics_scene)
        self.show()

    def load_this_ui(self):
        return os.path.join(os.path.dirname(__file__), __name__ + "_ui.ui")

    def show_gui(self):
        self.ui = QtCompat.loadUi(self.load_this_ui())
        if not self.ui:
            raise RuntimeError("Could not load UI from file path. Aborting...\n"
        self.ui.show()


class BaseNode(QtCore.QRect):
    def __init__(self, *args):
        super(MyRect, self).__init__(*args)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMoveable)

    def mousePressEvent(self, event=None):
        if event is None:
            event = QtWidgets.QGraphicsSceneMouseEvent()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    scene = QtWidgets.QGraphicsScene()
    pen = QtGui.QPen()
    brush = QtGui.QBrush(QtCore.Qt.green)
    view_instance = BaseView(scene)
    app.exec_()
