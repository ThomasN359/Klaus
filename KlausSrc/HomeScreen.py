from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtWidgets import *
from StatsWindow import StatsWindow
from ListCreatorWindow import ListCreatorWindow
from Settings import SettingsWindow
from GlobalThreads import ScheduleThread, BlockThread
from TodolistWindow import TodoListWindow
from NutritionWindow import NutritionWindow
from config import pictureDirectory
from HelperFunctions import makePath, create_button_with_pixmap


class HomeScreen(QMainWindow):
    def __init__(self, todo_list_archive, todo_list, block_lists, settings, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 1000, 800)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_lists = block_lists
        self.settings = settings
        self.setWindowTitle("Klaus")
        # Set the background image
        image_path = makePath(pictureDirectory, "plane.png")
        background_image = QPixmap(image_path)
        # Create a QPalette and set the QPixmap as its brush.
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(background_image))

        # Apply the palette to the window.
        self.setPalette(palette)

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

        # Todo List Button
        todolist_button = create_button_with_pixmap(makePath(pictureDirectory, "todolist.png"), (150, 150),
                                                    self.show_todolist)
        todolist_button.setStyleSheet("background-color: transparent; border: none;")
        todolist_label = QLabel('Todo List')
        todolist_label.setAlignment(Qt.AlignCenter)
        todolist_layout = QVBoxLayout()
        todolist_layout.addWidget(todolist_button)
        todolist_layout.addWidget(todolist_label)

        # Settings Button
        settings_button = create_button_with_pixmap(makePath(pictureDirectory, "setting.png"), (150, 150),
                                                    self.show_settings)
        settings_button.setStyleSheet("background-color: transparent; border: none;")
        settings_label = QLabel('Settings')
        settings_label.setAlignment(Qt.AlignCenter)
        settings_layout = QVBoxLayout()
        settings_layout.addWidget(settings_button)
        settings_layout.addWidget(settings_label)

        # List Creator Button
        list_creator_button = create_button_with_pixmap(makePath(pictureDirectory, "pencil.png"), (150, 150),
                                                        self.show_list_creator)
        list_creator_button.setStyleSheet("background-color: transparent; border: none;")
        list_creator_label = QLabel('List Creator')
        list_creator_label.setAlignment(Qt.AlignCenter)
        list_creator_layout = QVBoxLayout()
        list_creator_layout.addWidget(list_creator_button)
        list_creator_layout.addWidget(list_creator_label)

        # Stat Button
        stats_button = create_button_with_pixmap(makePath(pictureDirectory, "stats.png"), (150, 150), self.show_stats)
        stats_button.setStyleSheet("background-color: transparent; border: none;")
        stats_label = QLabel('Stats')
        stats_label.setAlignment(Qt.AlignCenter)
        stats_layout = QVBoxLayout()
        stats_layout.addWidget(stats_button)
        stats_layout.addWidget(stats_label)

        # Nutrition Button
        nutrition_button = create_button_with_pixmap(makePath(pictureDirectory, "nutrition.png"), (150, 150),
                                                     self.show_nutrition)
        nutrition_button.setStyleSheet("background-color: transparent; border: none;")
        nutrition_label = QLabel('Nutrition')
        nutrition_label.setAlignment(Qt.AlignCenter)
        nutrition_layout = QVBoxLayout()
        nutrition_layout.addWidget(nutrition_button)
        nutrition_layout.addWidget(nutrition_label)

        button_layout = QHBoxLayout()
        button_layout.addLayout(todolist_layout)
        button_layout.addLayout(settings_layout)
        button_layout.addLayout(list_creator_layout)
        button_layout.addLayout(stats_layout)
        button_layout.addLayout(nutrition_layout)

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
