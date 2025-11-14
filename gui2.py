import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("pyStereoMorph")

        button = QPushButton("Press Me!")

        #self.setFixedSize(QSize(400, 300))

        layout = QVBoxLayout()
        board_widget = BoardWidget({
                "type": "checkerboard",
                "nx": 3,
                "ny": 2,
            })

        # Set the central widget of the Window.

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(board_widget)


app = QApplication(sys.argv)

window = MainWindow()

window.show()

app.exec()