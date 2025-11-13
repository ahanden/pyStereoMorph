import sys

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import *
from PyQt6 import QtCore
from PyQt6.QtQuick import QQuickView

class CameraListItem(QObject):
    def __init__(self, camera_name, parent=None):
        super().__init__(parent)
        self.name = camera_name

    #@pyqtProperty('QString')
    def name(self):
        return self.name

class CameraList(QAbstractListModel):
    def __init__(self, cameras=[], parent=None):
        super().__init__(parent)
        self.cameras = cameras

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.cameras)

    def data(self, index: QModelIndex, role=None):
        # print(index, role)
        return self.cameras[index.row()]

    def addCamera(self, camera_name):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self.cameras.append(camera_name)
        self.endInsertRows()

app = QGuiApplication(sys.argv)

cameras = CameraList()
cameras.addCamera("Camera 1")
cameras.addCamera("Camera 2")
cameras.addCamera("Camera 3")
cameras.addCamera("Camera 4")
cameras.addCamera("Camera 5")
cameras.addCamera("Camera 6")

engine = QQmlApplicationEngine()
engine.quit.connect(app.quit)
engine.rootContext().setContextProperty('cameraModel', cameras)

#class CameraBtn:
class CameraBtn(QObject):
    def __init__(self):
        super().__init__()
        return
    @pyqtSlot()
    def click(self):
        cameras.addCamera(f"Camera {cameras.rowCount() + 1}")

btn = CameraBtn()
#engine.rootObjects()[0].setProperty('cameraBtn', btn)
engine.rootContext().setContextProperty('addCameraBtn', btn)

engine.load('main.qml')
sys.exit(app.exec())
