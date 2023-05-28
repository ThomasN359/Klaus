import os
import pickle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QHBoxLayout
from KlausSrc.Utilities.config import pickleDirectory
from KlausSrc.Utilities.HelperFunctions import makePath


from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLineEdit, QLabel, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class ChatWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.initUI()

    def initUI(self):
        # Create a vertical layout
        layout = QVBoxLayout()

        # Add a label
        label = QLabel("Klaus ChatBot", self)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Add a text edit widget for displaying chat history
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

        # Create a horizontal layout for the chat input
        self.chat_input_layout = QHBoxLayout()

        # Add a line edit for chat input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Chat Here")
        self.chat_input.setStyleSheet("background-color: rgba(255, 255, 255, 228);")  # 50% opacity white
        self.chat_input_layout.addWidget(self.chat_input)

        # Add a send button
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon('arrow.png'))  # Use your own image path
        self.send_button.clicked.connect(self.send_message)
        self.chat_input_layout.addWidget(self.send_button)

        # Add chat input layout to the main layout
        layout.addLayout(self.chat_input_layout)

        # Set the layout
        self.setLayout(layout)

    def send_message(self):
        message = self.chat_input.text()
        if message:  # If the message is not empty
            self.text_display.append("You: " + message)
            self.chat_input.clear()  # Clear the input field


