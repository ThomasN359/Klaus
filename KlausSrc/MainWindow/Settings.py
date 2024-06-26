from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import pickle
from KlausSrc.Utilities.config import pickleDirectory
import enum
from KlausSrc.Utilities.HelperFunctions import makePath

class KlausFeeling(enum.Enum):
    HAPPY = 1
    ANNOYED = 2
    ANGRY = 3
    VIOLENT = 4


class Settings:
    def __init__(self):
        self.daily_start_time = None
        self.browsers = []
        self.klaus_state = KlausFeeling.HAPPY
        self.enable_dialogue_reminder_window = True
        self.has_daily_update = False
        self.lock_in = False

class SettingsWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, block_list, settings):
        super().__init__()
        self.todo_list = todo_list
        self.block_list = block_list
        self.settings = settings
        self.todo_list_archive = todo_list_archive
        self.initUI()

    def initUI(self):
        # Create a QLabel widget for the title text
        self.title = QLabel("Settings", self)
        self.title.setAlignment(Qt.AlignHCenter)

        # Create a QTimeEdit widget for the daily start time
        self.start_time = QTimeEdit(self)
        self.start_time.setTime(self.settings.daily_start_time)
        self.start_time_label = QLabel("Set daily start time:", self)

        # Create a layout for the start time and its label
        self.start_time_layout = QHBoxLayout()
        self.start_time_layout.addWidget(self.start_time_label)
        self.start_time_layout.addWidget(self.start_time)


        self.enable_dialouge_reminder_checkbox = QCheckBox(self)
        self.enable_dialouge_reminder_checkbox.setChecked(self.settings.enable_dialogue_reminder_window)
        self.enable_dialouge_reminder_label = QLabel("Enable daily reminder dialogue windows when behind schedule")
        self.enable_dialouge_layout = QHBoxLayout()
        self.enable_dialouge_layout.addWidget(self.enable_dialouge_reminder_label)
        self.enable_dialouge_layout.addWidget(self.enable_dialouge_reminder_checkbox)

        # Create a layout for the start time and lock out widgets
        self.settings_layout = QVBoxLayout()
        self.settings_layout.addLayout(self.start_time_layout)
        self.settings_layout.addLayout(self.enable_dialouge_layout)

        # Create a layout for block site check box
        self.select_browser = QLabel("Choose the browsers you use ")
        self.chrome_label = QLabel("Chrome")
        self.msedge_label = QLabel("Microsoft Edge")
        self.brave_label = QLabel("Brave")
        self.chrome_box = QCheckBox(self)
        self.brave_box = QCheckBox(self)
        self.msedge_box = QCheckBox(self)
        self.brave_box.setChecked(self.settings.browsers[0])
        self.chrome_box.setChecked(self.settings.browsers[1])
        self.msedge_box.setChecked(self.settings.browsers[2])
        self.browser_check_layout = QHBoxLayout()
        self.browser_check_layout.addWidget(self.select_browser)
        self.browser_check_layout.addWidget(self.brave_label)
        self.browser_check_layout.addWidget(self.brave_box)
        self.browser_check_layout.addWidget(self.chrome_label)
        self.browser_check_layout.addWidget(self.chrome_box)
        self.browser_check_layout.addWidget(self.msedge_label)
        self.browser_check_layout.addWidget(self.msedge_box)
        self.settings_layout.addLayout(self.browser_check_layout)

        # Create a layout for the buttons
        self.buttons_layout = QHBoxLayout()

        # Create the "Back" button and connect it to the "go_back" slot
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        # self.buttons_layout.addWidget(self.back_button)

        # Create the "Save" button and connect it to the "save" slot
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        self.buttons_layout.addWidget(self.save_button)

        # Add the title, settings, and buttons layouts to the main layout of the widget
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.title)
        self.main_layout.addLayout(self.settings_layout)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.buttons_layout)
        self.setLayout(self.main_layout)

    def go_back(self):
        self.parent().initUI()
        self.close()

    def save(self):
        self.settings.daily_start_time = self.start_time.time()
        self.settings.enable_lock_out = self.lock_out.isChecked()
        # Brave, Chrome, Edge is the order
        self.settings.browsers = [self.brave_box.isChecked(), self.chrome_box.isChecked(), self.msedge_box.isChecked()]

        with open(makePath(pickleDirectory,'settings.pickle'), 'wb') as f:
            data = {"settings": self.settings, "type": "SETTINGS"}
            pickle.dump(data, f)
            f.flush()



