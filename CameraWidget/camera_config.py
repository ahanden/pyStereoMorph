
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIntValidator, QImage, QPixmap

import cv2

from CameraWidget.calibrate_camera import CameraCalibration

from CameraWidget.frame_painter import *

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

        sample_layout = QHBoxLayout()
        sample_layout.addWidget(QLabel("Calibration sample rate:"))
        self.sample_rate = QLineEdit()
        onlyInt = QIntValidator()
        onlyInt.setRange(1, 999)
        self.sample_rate.setValidator(onlyInt)
        sample_layout.addWidget(self.sample_rate)

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
        outer_layout.addLayout(sample_layout)
        outer_layout.addLayout(btn_layout)

        self.setLayout(outer_layout)

        self.update(config)

    def update(self, config):
        self.camera_name.setText(config['name'])
        self.rotation_input.setText(str(config['rotation']))
        self.video_file = config['video_file']
        self.sample_rate.setText(str(config['sample_rate']))
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
            "sample_rate": int(self.sample_rate.text()),
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
