import sys
from PySide6.QtWidgets import *

'''
Going to just start the design with the calibration ONLY.

I'm thinking a vertical layout. Top section is for the board.
Then a scrollable list of camera views.
At the bottom are buttons to add cameras and perform calibration.

+------------------------+
|Board Config            |
+------------------------+
|Camera List:            |
+------------------------+
|    Camera 1            |
+------------------------+
|    Camera 2            |
+------------+-----------+
| Add Camera | Calibrate |
+------------+-----------+


'''

from board_widget import BoardWidget
from CameraWidget.camera_widget import CameraList

board_config = {}
camera_configs = []

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("pyStereoMorph")

        button = QPushButton("Press Me!")

        #self.setFixedSize(QSize(400, 300))

        layout = QVBoxLayout()
        board_widget = BoardWidget({
                "type": "checkerboard",
                "nx": 8,
                "ny": 6,
            })
        board_widget.updated.connect(self.update_board_config)

        self.camera_list = CameraList()
        self.camera_list.set_board_params(board_widget.board_params)

        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Camera")
        add_btn.pressed.connect(self.camera_list.add_camera)
        calib_btn = QPushButton("Calibrate Cameras")
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(calib_btn)

        widget = QWidget()
        layout.addWidget(board_widget)
        layout.addWidget(self.camera_list)
        layout.addLayout(btn_layout)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def update_board_config(self, config):
        self.camera_list.set_board_params(config)

app = QApplication(sys.argv)

window = MainWindow()

window.show()

app.exec()
