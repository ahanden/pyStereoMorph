import generate_pattern as gp

from PySide6.QtCore import Signal
from PySide6.QtWidgets import *
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QIntValidator

class BoardDisplay(QWidget):
    def __init__(self, config):
        super().__init__()
        self.layout = QStackedLayout()

        # Eventually we should have a way to print the boards and all that.
        # For display, purposes, we don't.

        outer_layout = QHBoxLayout()
        stats_layout = QVBoxLayout()
        self.type_label = QLabel()
        self.nx_label = QLabel()
        self.ny_label = QLabel()


        self.config_btn = QPushButton("Settings")

        self.board_widget = QSvgWidget()
        self.board_widget.setMinimumSize(175, 124)
        self.board_widget.setMaximumSize(175, 124)

        self.update(config)

        stats_layout.addWidget(QLabel("Calibration Board:"))
        stats_layout.addWidget(self.type_label)
        stats_layout.addWidget(self.nx_label)
        stats_layout.addWidget(self.ny_label)
        stats_layout.addWidget(self.config_btn)
        outer_layout.addLayout(stats_layout)
        outer_layout.addWidget(self.board_widget)
        self.setLayout(outer_layout)

    def update(self, config):
        self.nx_label.setText(f"Interior horizontal corners: {config['nx']}")
        self.ny_label.setText(f"Interior vertical corners: {config['ny']}")
        self.type_label.setText(f"Board type: {config['type']}")
        width = config['nx'] + 1
        height = config['ny'] + 1
        self.board_img = gp.make_checkerboard_pattern(
            square_size=1,
            width=width,
            height=height,
            rows=width,
            cols=height,
        )

        self.board_widget.load(gp.render(self.board_img, width, height, vwidth=150, vheight=120))

class BoardConfig(QWidget):
    updated = Signal((int,), (str,))

    def __init__(self, config):
        super().__init__()

        input_layout = QGridLayout()

        onlyInt = QIntValidator()
        onlyInt.setRange(2, 99)

        input_layout.addWidget(QLabel("Interior horizontal corners:"), 0, 0)
        input_layout.addWidget(QLabel("Interior vertical corners:"), 1, 0)
        self.nx_input = QLineEdit(str(config['nx']))
        self.nx_input.setValidator(onlyInt)
        input_layout.addWidget(self.nx_input, 0, 1)
        self.ny_input = QLineEdit(str(config['ny']))
        self.ny_input.setValidator(onlyInt)
        input_layout.addWidget(self.ny_input, 1, 1)

        btn_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Save Changes")
        self.apply_btn.pressed.connect(lambda: self.updated.emite(True))
        btn_layout.addWidget(self.apply_btn)
        self.discard_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.discard_btn)

        outer_layout = QVBoxLayout()
        outer_layout.addLayout(input_layout)
        outer_layout.addLayout(btn_layout)
        self.setLayout(outer_layout)

    def update(self, config):
        self.nx_input.setText(str(config['nx']))
        self.y_input.setText(str(config['ny']))

    def get_config(self):
        return {
            "type": "checkerboard",
            "nx": int(self.nx_input.text()),
            "ny": int(self.ny_input.text()),
        }

class BoardWidget(QWidget):
    updated = Signal(bool)
    def __init__(self, board_params=None):
        super().__init__()

        if board_params is None:
            self.board_params = {
                "type": "checkerboard",
                "nx": 3,
                "ny": 2,
            }
        else:
            self.board_params = board_params

        outer_layout = QVBoxLayout()
        outer_layout.addWidget(QLabel("Board Settings:"))

        self.stack_layout = QStackedLayout()

        self.display_widget = BoardDisplay(self.board_params)
        self.display_widget.config_btn.pressed.connect(self.toggle_edit)

        self.config_widget = BoardConfig(self.board_params)
        self.config_widget.updated.connect(self.apply_changes)

        self.config_widget.discard_btn.pressed.connect(self.toggle_display)
        #self.config_widget.apply_btn.pressed.connect(self.apply_changes)


        self.stack_layout.addWidget(self.display_widget)
        self.stack_layout.addWidget(self.config_widget)

        outer_layout.addLayout(self.stack_layout)

        self.setLayout(outer_layout)

    def toggle_edit(self):
        self.stack_layout.setCurrentIndex(1)

    def toggle_display(self):
        self.stack_layout.setCurrentIndex(0)

    def apply_changes(self):
        self.board_params = self.config_widget.get_config()
        self.display_widget.update(self.board_params)
        self.stack_layout.setCurrentIndex(0)