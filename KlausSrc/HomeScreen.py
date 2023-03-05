from PyQt5.QtWidgets import QLabel
from KlausSrc import *
from Main import *
from ListCreatorWindow import *
from StatsWindow import *
from NutritionWindow import *

class HomeScreen(QMainWindow):
    def __init__(self, todo_list_archive, todo_list, block_lists, settings, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 1000, 800)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_lists = block_lists
        self.settings = settings
        self.setWindowTitle("Klaus")
        # self.setStyleSheet("background-color: #36393e;")
        self.initUI()

    def initUI(self):
        # Create a QLabel widget with the text "Create a Todolist to unlock chrome"
        # Set the text color to red using stylesheet
        label = QLabel("Create a Todolist to unlock the internet", self)
        label.setStyleSheet("color: red;")

        # If there are items in the block list, display the label
        if len(self.block_lists[0][0]) != 0:
            label.show()
        # Otherwise, hide the label
        else:
            label.hide()

        # T0do List Button
        todolist_button = QPushButton()
        pixmap = QPixmap(pictureDirectory + "/todolist.png")
        todolist_button.setIcon(QIcon(pixmap))
        todolist_button.setIconSize(QSize(150, 150))
        todolist_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        todolist_button.clicked.connect(self.show_todolist)

        # Settings Button
        settings_button = QPushButton()
        pixmap = QPixmap(pictureDirectory + "/setting.png")
        settings_button.setIcon(QIcon(pixmap))
        settings_button.setIconSize(QSize(150, 150))
        settings_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_button.clicked.connect(self.show_settings)

        # List Creator Button
        list_creator_button = QPushButton()
        pixmap = QPixmap(pictureDirectory + "/pencil.png")
        list_creator_button.setIcon(QIcon(pixmap))
        list_creator_button.setIconSize(QSize(150, 150))
        list_creator_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        list_creator_button.clicked.connect(self.show_list_creator)

        # Stat Button
        stats_button = QPushButton()
        pixmap = QPixmap(pictureDirectory + "/stats.png")
        stats_button.setIcon(QIcon(pixmap))
        stats_button.setIconSize(QSize(150, 150))
        stats_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        stats_button.clicked.connect(self.show_stats)

        # Nutrition Button
        nutrition_button = QPushButton()
        pixmap = QPixmap(pictureDirectory + "/nutrition.png")
        nutrition_button.setIcon(QIcon(pixmap))
        nutrition_button.setIconSize(QSize(150, 150))
        nutrition_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        nutrition_button.clicked.connect(self.show_nutrition)

        button_layout = QHBoxLayout()
        button_layout.addWidget(todolist_button)
        button_layout.addWidget(settings_button)
        button_layout.addWidget(list_creator_button)
        button_layout.addWidget(stats_button)
        button_layout.addWidget(nutrition_button)

        # Create a vertical box layout and add all the buttons to it
        vertical_layout = QVBoxLayout()
        vertical_layout.addStretch()
        vertical_layout.addWidget(label)
        vertical_layout.addLayout(button_layout)
        vertical_layout.addStretch()
        central_widget = QWidget(self)
        central_widget.setLayout(vertical_layout)
        self.setCentralWidget(central_widget)

    # Below are the functions for the main window class
    def show_stats(self):
        stats_window = StatsWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(stats_window)

    def show_nutrition(self):
        nutrition_window = NutritionWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(nutrition_window)

    def show_todolist(self):
        todolist_window = TodoListWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        self.setCentralWidget(todolist_window)

    def show_settings(self):
        settings_window = SettingsWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        self.setCentralWidget(settings_window)

    def show_list_creator(self):
        list_creator_window = ListCreatorWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(list_creator_window)

    def start_scheduling(self):
        self.schedule_thread = ScheduleThread(self.todo_list, self.settings, self)
        self.schedule_thread.start()

    def start_blocking(self):
        self.block_thread = BlockThread(self.block_lists, self)
        self.block_thread.start()
