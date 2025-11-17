
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIntValidator

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
    thumbnail_height = 128
    thumbnail_width = frame.shape[1] * thumbnail_height // frame.shape[0]
    frame = cv2.resize(frame, (thumbnail_width, thumbnail_height))
    thumbnail = QImage(
        frame,
        frame.shape[1],
        frame.shape[0],
        QImage.Format.Format_BGR888,
    )
    return QPixmap.fromImage(thumbnail)

class CameraDisplay(QWidget):
    def __init__(self, config):
        super().__init__()

        layout = QVBoxLayout()

        self.name_label = QLabel()
        self.video_path = QLabel()
        self.video_frame = QLabel()
        self.edit_btn = QPushButton("Settings")
        self.calib_btn = QPushButton("Calibrate")
        self.calib_btn.pressed.connect(self.calibrate)


        layout.addWidget(self.name_label)
        layout.addWidget(self.video_path)
        layout.addWidget(self.video_frame)

        self.calib_stack = QStackedLayout()

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.edit_btn)
        btn_layout.addWidget(self.calib_btn)
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        self.calib_stack.addWidget(btn_widget)

        #policy = QSizePolicy()
        #policy.setRetainSizeWhenHidden(True)
        #self.calib_btn.setSizePolicy(policy)
        #self.calib_btn.hide()

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
            self.video_frame.setPixmap(frame_data)
            self.video_frame.setMinimumSize(
                frame_data.rect().height(),
                frame_data.rect().width(),
            )
        else:
            self.video_path.setText("Missing calibration video file")

    def calibrate(self):
        self.cc = CameraCalibration(
            #"D:\\StereoMorph\\stereomorph\\Calibrate_videos\\A_ppv_scale.avi",
            "D:\\StereoMorph\\stereomorph\\Calibrate_videos\\C_scale_lateral.avi",
            7, 6, # FIX THIS
            0,
            False,
            False,
        )
        self.calib_stack.setCurrentIndex(1)
        self.cc.progress.connect(self.progress_bar.setValue)
        self.cc.finished.connect(lambda: self.calib_stack.setCurrentIndex(0))
        self.cc.finished.connect(self.cc.deleteLater)
        self.cc.start()



class CameraConfig(QWidget):
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
        self.cancel_btn = QPushButton("Cancel")
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
        #filename = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
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
            self.video_frame_label.setPixmap(frame_data)
            self.video_frame_label.setMinimumSize(
                frame_data.rect().height(),
                frame_data.rect().width(),
            )

class CameraWidget(QWidget):
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stack_layout = QStackedLayout()

        self.camera_display = CameraDisplay(config)
        self.camera_display.edit_btn.pressed.connect(self.toggle_config)
        self.camera_config = CameraConfig(config)
        self.camera_config.cancel_btn.pressed.connect(self.toggle_display)
        self.camera_config.submit_btn.pressed.connect(self.update_config)

        self.stack_layout.addWidget(self.camera_display)
        self.stack_layout.addWidget(self.camera_config)

        self.setLayout(self.stack_layout)

    def toggle_display(self):
        self.stack_layout.setCurrentIndex(0)

    def toggle_config(self):
        self.stack_layout.setCurrentIndex(1)

    def update_config(self):
        self.config = self.camera_config.get_config()
        self.camera_display.update(self.config)
        self.toggle_display()

    def get_config(self):
        return self.camera_config.get_config()

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
        self.scroll_area_layout.addWidget(camera_widget)