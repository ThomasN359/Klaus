from PyQt5.QtWidgets import QLabel, QPushButton

from KlausSrc import *
from Main import *

class StatsWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Create a QLabel widget and set its text
        label = QLabel(self)
        label.setText("This is the User Stats window")
        label.setAlignment(Qt.AlignCenter)

        # Create a layout for the buttons
        buttons_layout = QHBoxLayout()

        # Create the "Back" button and connect it to the "go_back" slot
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        buttons_layout.addWidget(self.back_button)

        # Add the buttons layout to the main layout of the widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def go_back(self):
        self.parent().initUI()