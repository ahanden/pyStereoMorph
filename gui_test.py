import sys

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import *
from PyQt6 import QtCore
from PyQt6.QtQuick import QQuickView

class CameraConfig(QObject):
    def __init__(self, camera_name, parent=None):
        super().__init__(parent)
        self._name = camera_name
        self.rotation = None
        self.flip_v = False
        self.flip_h = False
        self.filename = None

    @pyqtSlot(str)
    def name(self):
        return self._name

class CameraList(QAbstractListModel):
    def __init__(self, cameras=[], parent=None):
        super().__init__(parent)
        self.cameras = cameras

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.cameras)

    def data(self, index: QModelIndex, role=None):
        return self.cameras[index.row()]

    def addCamera(self, camera_name):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        #self.cameras.append(CameraConfig(camera_name))
        self.cameras.append({
            "name": camera_name,
            "rotation": None,
            "flip_v": False,
            "flip_h": False,
            "calibrate_file": None,
        })
        self.endInsertRows()

class FocusArea(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_camera_config = cameras.cameras[0]

    def focus(self, index):
        self.active_camera_config = cameras.cameras[index]

    @pyqtSlot()
    def config(self):
        return self.active_camera_config

    @pyqtSlot()
    def name(self):
        return self.active_camera_config['name']

app = QGuiApplication(sys.argv)

cameras = CameraList()
cameras.addCamera("Camera 1")
cameras.addCamera("Camera 2")

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
engine.rootContext().setContextProperty('cameraModel', cameras)
focus_area = FocusArea()
engine.rootContext().setContextProperty('focusArea', focus_area)

#class CameraBtn:
class CameraBtn(QObject):
    def __init__(self):
        super().__init__()
        return
    @pyqtSlot()
    def click(self):
        cameras.addCamera(f"Camera {cameras.rowCount() + 1}")

btn = CameraBtn()
engine.rootContext().setContextProperty('addCameraBtn', btn)

def new_focus(i):
    active_camera = cameras.cameras[i]
engine.rootContext().setContextProperty('focusConfig', new_focus)

engine.load('main.qml')
sys.exit(app.exec())
