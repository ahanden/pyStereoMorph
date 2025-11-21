
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIntValidator, QImage, QPixmap

import cv2

from CameraWidget.camera_display import CameraDisplay
from CameraWidget.camera_config import CameraConfig
from CameraWidget.calibrate_camera import CameraCalibration

def reorient(frame, rotate=0, v_flip=False, h_flip=False):
    if rotate % 360:
        height, width = frame.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D(
            (width // 2, height // 2),
            rotate,
            1.0,
        )
        frame = cv2.warpAffine(
            frame,
            rotation_matrix,
            (width, height),
        )
    if v_flip:
        frame = cv2.flip(frame, 0)
    if h_flip:
        frame = cv2.flip(frame, 1)
    return frame

def get_first_frame(filename, rotate=0, v_flip=False, h_flip=False):
    video = cv2.VideoCapture(filename)
    status, frame = video.read()
    frame = reorient(frame, rotate, v_flip,h_flip)
    return frame

def paint_frame(widget, frame):
    thumbnail_height = 128
    thumbnail_width = frame.shape[1] * thumbnail_height // frame.shape[0]
    frame = cv2.resize(frame, (thumbnail_width, thumbnail_height))
    thumbnail = QImage(
        frame,
        frame.shape[1],
        frame.shape[0],
        QImage.Format.Format_BGR888,
    )
    widget.setPixmap(QPixmap.fromImage(thumbnail))
    widget.setMinimumSize(*frame.shape[:2])

class CameraWidget(QWidget):
    updated = Signal(dict)
    delete = Signal(int)
    def __init__(self, cam_id, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = cam_id

        self.calibration = False
        self.config = {}
        self.stack_layout = QStackedLayout()

        self.camera_display = CameraDisplay(config)
        self.camera_display.request_edit.connect(self.toggle_config)
        self.camera_display.start_calibration.connect(self.calibrate)
        self.camera_display.calibrated.connect(self.update_calibration)
        self.camera_display.delete.connect(lambda: self.delete.emit(self.id))
        self.camera_config = CameraConfig(config)
        self.camera_config.cancelled.connect(self.toggle_display)
        self.camera_config.updated.connect(self.update_config)

        self.stack_layout.addWidget(self.camera_display)
        self.stack_layout.addWidget(self.camera_config)

        self.setLayout(self.stack_layout)

    def set_board_config(self, config):
        self.board_config = config

    def update_calibration(self, calib):
        self.calibration = calib

    def toggle_display(self):
        self.stack_layout.setCurrentIndex(0)

    def toggle_config(self):
        self.stack_layout.setCurrentIndex(1)

    def update_config(self, config):
        same = True
        for key in config.keys():
            if self.config.get(key, None) != config[key]:
                same = False
                break
        if not same:
            self.config = config
            self.camera_display.update(self.config)
            self.camera_display.calib_msg.setText("Not calibrated")
        self.updated.emit(config)
        self.toggle_display()

    def get_config(self):
        return self.camera_config.get_config()

    def calibrate(self):
        self.camera_display.calib_msg.clear()
        camera_config = self.get_config()
        self.cc = CameraCalibration(
            camera_config['video_file'],
            self.board_config['nx'],
            self.board_config['ny'],
            camera_config['rotation'],
            camera_config['v_flip'],
            camera_config['h_flip'],
            camera_config['sample_rate'],
            camera_config['distorted'],
        )
        self.camera_display.calib_stack.setCurrentIndex(1)
        self.cc.progress.connect(self.camera_display.update_calibrate_progress)
        self.cc.finished.connect(self.done_calibrating)
        self.cc.finished.connect(self.cc.deleteLater)
        self.cc.start()

    def done_calibrating(self):
        self.camera_display.calib_stack.setCurrentIndex(0)
        self.calibration = self.cc.get_calibration()
        frames = len(self.calibration['frames_with_corners'])
        if self.calibration['mtx'] is not None:
            self.camera_display.calib_msg.setText(f"Calibration successful with {frames} frames")
        else:
            self.camera_display.calib_msg.setText(f"Calibration failed with {frames} frames")
        #self.camera_display.calib_frame.clear()
        #self.calibrated.emit((mtx, dist))

class CameraList(QWidget):
    def __init__(self):
        super().__init__()

        self.camera_list = []

        layout = QVBoxLayout()

        label = QLabel("Camera List")
        layout.addWidget(label)

        scroll_area = QScrollArea()
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        scroll_widget.setLayout(self.scroll_area_layout)
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        self.setLayout(layout)

        self.add_camera()
        self.add_camera()

    def add_camera(self):
        if self.camera_list:
            cam_id = max((cam.id for cam in self.camera_list)) + 1
            cam_names = {cam.get_config()['name'] for cam in self.camera_list}
            cam_index = cam_id
            name = f"Camera {cam_index}"
            while name in cam_names:
                cam_index += 1
                name = f"Camera {cam_index}"
        else:
            cam_id = 1
            name = "Camera 1"

        camera_widget = CameraWidget(cam_id, {
            "name": name,
            "rotation": 0,
            "v_flip": False,
            "h_flip": False,
            "distorted": False,
            "video_file": '',
            "sample_rate": 1,
        })
        self.camera_list.append(camera_widget)
        camera_widget.delete.connect(self.delete_camera)
        self.scroll_area_layout.addWidget(camera_widget)

    def delete_camera(self, cam_id):
        idx = next(idx for idx, cam in enumerate(self.camera_list) if cam.id == cam_id)
        cam = self.scroll_area_layout.takeAt(idx)
        self.camera_list.pop(idx)
        cam.widget().deleteLater()

    def set_board_params(self, board_config):
        self.board_config = board_config
        for widget in self.camera_list:
            widget.set_board_config(board_config)
