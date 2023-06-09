from PyQt5.uic.Compiler.qtproxies import QtCore
import random
from KlausSrc.Utilities.HelperFunctions import save_setting
from KlausSrc.MainWindow.Settings import *


class ReminderPopUp(QDialog):
    def __init__(self, klaus_feeling, parent=None):
        super().__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
        self.klaus_feeling = klaus_feeling

        # Set up the layout
        layout = QVBoxLayout(self)
        self.setWindowTitle("Work Reminder")

        # Generate random x and y coordinates for the dialog's position
        screen = QDesktopWidget().screenGeometry()
        x = random.randint(0, screen.width() - self.width())
        y = random.randint(0, screen.height() - self.height())
        self.setGeometry(x // 3, y // 2, 1000, 1000)

        # Add a message label
        message_label = QLabel("Reminder to complete the task", self)
        if self.klaus_feeling == KlausFeeling.ANNOYED:
            message_label.setStyleSheet("font-size: 30px; color: yellow;")
        elif self.klaus_feeling == KlausFeeling.ANGRY:
            message_label.setStyleSheet("font-size: 50px; color: orange;")
        elif self.klaus_feeling == KlausFeeling.VIOLENT:
            message_label.setStyleSheet("font-size: 100px; color: red;")

        layout.addWidget(message_label)

        # Add a button to close the dialog
        close_button = QPushButton("OK", self)
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)


class LockInPopUp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings
        if self.settings.lock_in == False:
            self.setWindowTitle("Lock In Pop-Up")

            layout = QVBoxLayout()

            message_label = QLabel("By locking the todo-list you can no longer remove unwanted tasks?")
            layout.addWidget(message_label)

            yes_button = QPushButton("Yes")
            yes_button.clicked.connect(self.yes_button_clicked)
            layout.addWidget(yes_button)

            no_button = QPushButton("No")
            no_button.clicked.connect(self.no_button_clicked)
            layout.addWidget(no_button)

            self.setLayout(layout)
        else:
            layout = QVBoxLayout()
            message_label = QLabel("It is currently locked")
            ok_button = QPushButton("Ok")
            ok_button.clicked.connect(self.no_button_clicked)
            layout.addWidget(message_label)
            layout.addWidget(ok_button)
            self.setLayout(layout)

    def yes_button_clicked(self):
        self.settings.lock_in = True
        self.parent().refresh_save()
        save_setting(self.settings)
        print("Lock in set to true")
        self.close()


    def no_button_clicked(self):
        self.close()
        print("Closed popup window")

