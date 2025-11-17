
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIntValidator, QImage, QPixmap

import cv2

from calibrate_camera import CameraCalibration

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

class CameraDisplay(QWidget):
    request_edit = Signal(bool)
    start_calibration = Signal(bool)
    calibrated = Signal(tuple)
    def __init__(self, config):
        super().__init__()

        layout = QVBoxLayout()

        self.name_label = QLabel()
        self.video_path = QLabel()
        self.edit_btn = QPushButton("Settings")
        self.edit_btn.pressed.connect(lambda: self.request_edit.emit(True))
        self.calib_btn = QPushButton("Calibrate")
        self.calib_btn.pressed.connect(lambda: self.start_calibration.emit(True))
        self.calib_btn.setEnabled(False)

        layout.addWidget(self.name_label)
        layout.addWidget(self.video_path)

        frame_layout = QHBoxLayout()
        self.video_frame = QLabel()
        frame_layout.addWidget(self.video_frame)
        self.calib_frame = QLabel()
        frame_layout.addWidget(self.calib_frame)
        layout.addLayout(frame_layout)

        self.calib_stack = QStackedLayout()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.calib_btn)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        self.calib_stack.addWidget(btn_widget)

        self.calib_msg = QLabel("Not calibrated")
        layout.addWidget(self.calib_msg)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.calib_stack.addWidget(self.progress_bar)

        layout.addLayout(self.calib_stack)

        self.setLayout(layout)

        self.update(config)

    def update(self, config):
        self.name_label.setText(config['name'])
        if config['video_file']:
            self.video_path.setText(config['video_file'])
            frame_data = get_first_frame(
                config['video_file'],
                config['rotation'],
                config['v_flip'],
                config['h_flip'],
            )
            paint_frame(self.video_frame, frame_data)
            self.calib_btn.setEnabled(True)
        else:
            self.video_path.setText("Missing calibration video file")
            self.calib_btn.setEnabled(False)

    def update_calibrate_progress(self, args):
        progress, frame = args
        self.progress_bar.setValue(progress)
        paint_frame(self.calib_frame, frame)



class CameraConfig(QWidget):
    updated = Signal(dict)
    cancelled = Signal(bool)
    def __init__(self, config):
        super().__init__()

        outer_layout = QVBoxLayout()

        name_row_layout = QHBoxLayout()
        name_row_layout.addWidget(QLabel("Camera Name:"))
        self.camera_name = QLineEdit()
        name_row_layout.addWidget(self.camera_name)

        self.video_frame_label = QLabel()

        file_row_layout = QHBoxLayout()
        self.video_file = config['video_file']
        self.file_label = QLabel()
        chooser_btn = QPushButton("Select Calibration File")
        chooser_btn.pressed.connect(self.open_file_chooser)
        file_row_layout.addWidget(self.file_label)
        file_row_layout.addWidget(chooser_btn)

        orient_layout = QHBoxLayout()
        orient_layout.addWidget(QLabel("Reorient:"))
        orient_layout.addWidget(QLabel("Rotate (degrees):"))
        self.rotation_input = QLineEdit()
        self.rotation_input.editingFinished.connect(self.update_frame)
        orient_layout.addWidget(self.rotation_input)
        self.vflip_input = QCheckBox("flip veritcally")
        self.vflip_input.checkStateChanged.connect(self.update_frame)
        self.hflip_input = QCheckBox("flip horizontally")
        self.hflip_input.checkStateChanged.connect(self.update_frame)
        orient_layout.addWidget(self.vflip_input)
        orient_layout.addWidget(self.hflip_input)

        self.submit_btn = QPushButton("Save Changes")
        self.submit_btn.pressed.connect(lambda: self.updated.emit(self.get_config()))
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.pressed.connect(lambda: self.cancelled.emit(True))
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.cancel_btn)

        outer_layout.addLayout(name_row_layout)
        outer_layout.addWidget(self.video_frame_label)
        outer_layout.addLayout(file_row_layout)
        outer_layout.addLayout(orient_layout)
        outer_layout.addLayout(btn_layout)

        self.setLayout(outer_layout)

        self.update(config)

    def update(self, config):
        self.camera_name.setText(config['name'])
        self.rotation_input.setText(str(config['rotation']))
        self.video_file = config['video_file']
        if self.video_file:
            self.file_label.setText(config['video_file'])
        else:
            self.file_label.setText("Missing calibration video file")
        self.vflip_input.setCheckState(Qt.CheckState.Checked if config['v_flip'] else Qt.CheckState.Unchecked)
        self.hflip_input.setCheckState(Qt.CheckState.Checked if config['h_flip'] else Qt.CheckState.Unchecked)

    def get_config(self):
        name = self.camera_name.text().strip()

        try:
            rotation = int(self.rotation_input.text())
        except ValueError:
            rotation = 0

        return {
            "name": name,
            "rotation": rotation,
            "v_flip": self.vflip_input.checkState() == Qt.CheckState.Checked,
            "h_flip": self.hflip_input.checkState() == Qt.CheckState.Checked,
            "video_file": self.video_file,
        }

    def open_file_chooser(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File")
        if filename:
            self.video_file = filename
            self.update_frame()

    def update_frame(self):
        if self.video_file:
            self.file_label.setText(self.video_file)
            config = self.get_config()
            frame_data = get_first_frame(
                self.video_file,
                config['rotation'],
                config['v_flip'],
                config['h_flip'],
            )
            paint_frame(self.video_frame_label, frame_data)

class CameraWidget(QWidget):
    updated = Signal(dict)
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.calibration = False
        self.config = {}
        self.stack_layout = QStackedLayout()

        self.camera_display = CameraDisplay(config)
        self.camera_display.request_edit.connect(self.toggle_config)
        self.camera_display.start_calibration.connect(self.calibrate)
        self.camera_display.calibrated.connect(self.update_calibration)
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
        )
        self.camera_display.calib_stack.setCurrentIndex(1)
        self.cc.progress.connect(self.camera_display.update_calibrate_progress)
        self.cc.finished.connect(self.done_calibrating)
        self.cc.finished.connect(self.cc.deleteLater)
        self.cc.start()

    def done_calibrating(self):
        self.camera_display.calib_stack.setCurrentIndex(0)
        mtx = self.cc.mtx
        dist = self.cc.dist
        frames = self.cc.frames_with_corners
        if mtx is not None:
            self.camera_display.calib_msg.setText(f"Calibration successful with {frames} frames")
        else:
            self.camera_display.calib_msg.setText(f"Calibration failed with {frames} frames")
        self.camera_display.calib_frame.clear()
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
        index = self.scroll_area_layout.count() + 1
        camera_widget = CameraWidget({
            "name": f"Camera {index}",
            "rotation": 0,
            "v_flip": False,
            "h_flip": False,
            "video_file": '',
        })
        self.camera_list.append(camera_widget)
        self.scroll_area_layout.addWidget(camera_widget)

    def set_board_params(self, board_config):
        self.board_config = board_config
        for widget in self.camera_list:
            widget.set_board_config(board_config)
