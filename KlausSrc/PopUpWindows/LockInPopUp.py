from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

from KlausSrc.Utilities.HelperFunctions import save_setting


class LockInPopUp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: none;")
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

