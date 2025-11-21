
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIntValidator, QImage, QPixmap

import cv2

from CameraWidget.calibrate_camera import CameraCalibration
from CameraWidget.frame_painter import *

class CameraDisplay(QWidget):
    request_edit = Signal(bool)
    start_calibration = Signal(bool)
    delete = Signal(bool)
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
        self.del_btn = QPushButton("Delete")
        self.del_btn.pressed.connect(lambda: self.delete.emit(True))

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
        btn_layout.addWidget(self.del_btn)
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
        progress, frame, msg = args
        self.progress_bar.setValue(progress)
        if frame is not None:
            paint_frame(self.calib_frame, frame)
