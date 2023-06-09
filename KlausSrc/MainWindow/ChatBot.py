import os
import pickle
from PyQt5.QtCore import QTimer, pyqtSignal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QHBoxLayout, \
    QScrollBar, QScrollArea
from PyQt5.QtGui import QKeyEvent, QIcon
from KlausSrc.Utilities.config import pickleDirectory
from KlausSrc.Utilities.HelperFunctions import makePath

class MessageLabel(QLabel):
    def __init__(self, text):
        super().__init__()
        self.setText(text)
        self.setWordWrap(True)
        self.setStyleSheet("background-color: white; border-radius: 5px; padding: 5px;")
        self.setContentsMargins(5, 5, 5, 5)


class ChatWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        label = QLabel("Klaus", self)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        # Create a separate QWidget for the chat display area
        self.chat_display_widget = QWidget()
        self.scroll_area.setWidget(self.chat_display_widget)

        # Add border to chat_display_widget
        self.chat_display_widget.setStyleSheet("border: 2px solid black")

        # Create a QVBoxLayout for the chat display widget
        self.chat_display_layout = QVBoxLayout()
        self.chat_display_layout.setAlignment(Qt.AlignTop)
        self.chat_display_widget.setLayout(self.chat_display_layout)

        self.chat_input_layout = QHBoxLayout()

        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Chat Here")
        self.chat_input.setStyleSheet("background-color: rgba(255, 255, 255, 228);")
        self.chat_input.keyPressEvent = self.on_key_press  # Intercept the key press event
        self.chat_input_layout.addWidget(self.chat_input)

        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon('arrow.png'))
        self.send_button.clicked.connect(self.send_message)
        self.chat_input_layout.addWidget(self.send_button)

        layout.addLayout(self.chat_input_layout)

        self.setLayout(layout)

        # Add border to main widget
        self.setStyleSheet("border: 2px solid black")

    def on_key_press(self, event: QKeyEvent):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.send_message()
        else:
            QLineEdit.keyPressEvent(self.chat_input, event)  # Default handler

    def send_message(self):
        message = self.chat_input.text()
        if message:
            self.display_message("You: " + message)
            self.display_message("Klaus: I have yet to be trained")
            self.chat_input.clear()

    def display_message(self, message: str):
        message_label = MessageLabel(message)
        self.chat_display_layout.addWidget(message_label)


