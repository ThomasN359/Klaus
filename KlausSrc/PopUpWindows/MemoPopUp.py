from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QTextEdit, QLabel, QDialog, QVBoxLayout


class MemoPopUp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings
        self.setWindowTitle("Memo Pop-Up")
        self.setStyleSheet("background-color: none;")

        # Create main layout
        layout = QVBoxLayout()

        # Create QLabel and add it to the layout
        message_label = QLabel("Write and save a memo for this day. These logs will be sent\n to other user stats and can"
                               " be viewed in other windows later.\n Note no code is done besides \nthe UI so saving doesn't "
                               "do anything")
        layout.addWidget(message_label)

        # Create large text field (QTextEdit) and add it to the layout
        self.text_field = QTextEdit()
        layout.addWidget(self.text_field)

        # Create Save and Close buttons, and their layout
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_clicked)
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(close_button)

        # Add buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Set main layout
        self.setLayout(layout)

    def save_clicked(self):
        # Update button text and style sheet
        self.save_button.setText('Saved')
        self.save_button.setStyleSheet('background-color: green')

        # Create a QTimer to revert the changes after one second
        QTimer.singleShot(1000, self.reset_save_button)

    def reset_save_button(self):
        # Revert button text and style sheet
        self.save_button.setText('Save')
        self.save_button.setStyleSheet('')