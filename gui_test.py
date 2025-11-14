import sys

from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import *
from PyQt6 import QtCore
from PyQt6.QtQuick import QQuickView
from PySide6.QtWidgets import QLabel

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtQml import *

from PySide6.QtCore import QObject, Slot
from PySide6.QtQml import QmlElement

import cv2

QML_IMPORT_NAME = "io.qt.textproperties"
QML_IMPORT_MAJOR_VERSION = 1


@QmlElement
class VideoFrame(QObject):
    pyqtSlot

    @Slot(str)
    def setVideo(self, filename):
        video = cv2.VideoCapture(video_filename)
        status, frame = video.read()
        thumbnail_height = 128
        thumbnail_width = frame.shape[1] * thumbnail_height // frame.shape[0]
        frame = cv2.resize(frame, (thumbnail_width, thumbnail_height))

        thumbnail = QImage(
            frame,
            frame.shape[1],
            frame.shape[0],
            QImage.Format.Format_BGR888,
        )
        this.setPixmap(QPixmap.fromImage(thumbnail))

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
        self.cameras.append({
            "name": camera_name,
            "rotation": '',
            "flip_v": False,
            "flip_h": False,
            "calibrate_file": '',
        })
        self.endInsertRows()

    @pyqtSlot(int, str, str, bool, bool, str)
    def updateCamera(self, index, name, rotation, flip_v, flip_h, calibrate_file):
        self.cameras[index] = {
            "name": name,
            "rotation": rotation,
            "flip_v": flip_v,
            "flip_h": flip_h,
            "calibrate_file": calibrate_file,
        }

app = QGuiApplication(sys.argv)

cameras = CameraList()
cameras.addCamera("Camera 1")
cameras.addCamera("Camera 2")

engine = QQmlApplicationEngine()
engine.addImportPath(sys.path[0])
engine.loadFromModule("QmlIntegration", "VideoFrame")
engine.quit.connect(app.quit)
engine.rootContext().setContextProperty('cameraModel', cameras)

class CameraBtn(QObject):
    def __init__(self):
        super().__init__()
        return
    @pyqtSlot()
    def click(self):
        cameras.addCamera(f"Camera {cameras.rowCount() + 1}")

btn = CameraBtn()
engine.rootContext().setContextProperty('addCameraBtn', btn)

engine.load('main.qml')
sys.exit(app.exec())
