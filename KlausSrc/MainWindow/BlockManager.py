import enum
import os
import pickle
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from qtwidgets import Toggle, AnimatedToggle
from KlausSrc.PopUpWindows.ListCreatorPopUp import ListCreatorPopUp
from KlausSrc.Utilities.config import pickleDirectory
from KlausSrc.Utilities.HelperFunctions import makePath


class ListStatus(enum.Enum):
    ON = 0
    OFF = 1
    TIMERON = 2
class BlockManagerWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, block_list, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_list = block_list
        self.initUI()

    def initUI(self):
        # Create a label for "Block List Manager"
        title_label = QLabel("Block List Manager")
        title_label.setAlignment(Qt.AlignCenter)  # Center the label horizontally
        title_label.setFont(QFont("Arial", 16))  # Increase font size

        # Set up the main window layout
        layout = QVBoxLayout()
        layout.addWidget(title_label)

        # Create labels and custom switches for "App Block List"
        app_list_label = QLabel("App Block List")
        layout.addWidget(app_list_label)
        for key, (web_list, is_active) in self.block_list[0].items():
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(key))
            animated_toggle = AnimatedToggle(
                checked_color="#00FF00",  # Green color
                pulse_checked_color="#4400FF00"  # Green color with transparency
            )  # Create the animated toggle switch
            animated_toggle.setFixedSize(80, 60)  # Adjust the width and height
            animated_toggle.setChecked(is_active == ListStatus.ON)
            hbox.addWidget(animated_toggle)
            layout.addLayout(hbox)

        # Create labels and custom switches for "Web Block List"
        web_list_label = QLabel("Web Block List")
        layout.addWidget(web_list_label)
        for key, (web_list, is_active) in self.block_list[1].items():
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(key))
            animated_toggle = AnimatedToggle(
                checked_color="#00FF00",  # Green color
                pulse_checked_color="#4400FF00"  # Green color with transparency
            )  # Create the animated toggle switch
            animated_toggle.setFixedSize(40, 20)  # Adjust the width and height
            animated_toggle.setChecked(is_active == ListStatus.ON)
            hbox.addWidget(animated_toggle)
            layout.addLayout(hbox)

        # Create a button to open the pop-up
        open_list_creator_button = QPushButton("Add Block List")
        open_list_creator_button.clicked.connect(self.add_block_list)
        layout.addWidget(open_list_creator_button)

        self.setLayout(layout)

    def add_block_list(self):
        list_creator_pop_up = ListCreatorPopUp(self, self.todo_list_archive, self.todo_list, self.block_list)
        list_creator_pop_up.exec_()  # Show the pop-up dialog as modal
