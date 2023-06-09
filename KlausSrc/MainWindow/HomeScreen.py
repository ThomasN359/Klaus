from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtWidgets import *
from KlausSrc.GlobalModules.GlobalThreads import kill_timer_thread2
from KlausSrc.MainWindow.StatsWindow import StatsWindow
from KlausSrc.MainWindow.ListCreatorWindow import ListCreatorWindow
from KlausSrc.MainWindow.Settings import SettingsWindow
from KlausSrc.GlobalModules.GlobalThreads import ScheduleThread, BlockThread
from KlausSrc.MainWindow.TodolistWindow import TodoListWindow
from KlausSrc.MainWindow.NutritionWindow import NutritionWindow
from KlausSrc.Utilities.config import iconDirectory, wallpaperDirectory
from KlausSrc.Utilities.HelperFunctions import makePath, create_button_with_pixmap
from KlausSrc.MainWindow.ChatBot import ChatWindow
from KlausSrc.GlobalModules.GlobalThreads import shared_state
from PyQt5.QtWidgets import QMainWindow, QDockWidget, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QBrush, QPalette



def create_centered_button_layout(button, label):
    widget = QWidget()
    layout = QHBoxLayout(widget)

    layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
    layout.addWidget(button)
    layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

    button_layout = QVBoxLayout()
    button_layout.addWidget(widget)
    button_layout.addWidget(label)

    return button_layout



class HomeScreen(QMainWindow):
    def __init__(self, todo_list_archive, todo_list, block_lists, settings,  window_number, parent=None):
        super().__init__(parent)
        self.window_number = window_number
        #self.setStyleSheet("background-color: transparent; border: none;") if you want wallpapers it should be transparent
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_lists = block_lists
        self.settings = settings
        self.setWindowTitle("Klaus")

        # # Set the background image
        # image_path = makePath(wallpaperDirectory, "plane.png")
        # background_image = QPixmap(image_path)
        #
        # # Scale the background image to fit the window
        # scaled_image = background_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        #
        # # Create a QPalette and set the QPixmap as its brush.
        # palette = QPalette()
        # palette.setBrush(QPalette.Background, QBrush(scaled_image))
        #
        # # Apply the palette to the window.
        # self.setPalette(palette)

        self.sidebar_visible = True
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

        # Create the sidebar widget
        if self.window_number == 1:
            sidebar_widget = QWidget(self)
            sidebar_widget.setStyleSheet("background-color: #cfcfcf;")
            sidebar_layout  = QVBoxLayout(sidebar_widget)


        if self.window_number == 1:
            # Add expand/shrink button to the sidebar layout
            expand_button = QPushButton("≡", self)
            expand_button.clicked.connect(self.toggle_sidebar_size)
            expand_button.setFixedSize(30, 30)
            expand_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            sidebar_layout.addWidget(expand_button)

        # Add sidebar buttons to the sidebar layout
        self.todolist_button = create_button_with_pixmap(makePath(iconDirectory, "todolist.png"), (110, 110),
                                                    self.show_todolist)
        self.todolist_button.setStyleSheet("background-color: transparent; border: none;")
        self.todolist_label = QLabel('Todo List')
        self.todolist_label.setAlignment(Qt.AlignCenter)
        self.todolist_layout = create_centered_button_layout(self.todolist_button, self.todolist_label)
        self.settings_button = create_button_with_pixmap(makePath(iconDirectory, "setting.png"), (110, 110),
                                                    self.show_settings)
        self.settings_button.setStyleSheet("background-color: transparent; border: none;")
        self.settings_label = QLabel('Settings')
        self.settings_label.setAlignment(Qt.AlignCenter)
        self.settings_layout = create_centered_button_layout(self.settings_button, self.settings_label)
        self.list_creator_button = create_button_with_pixmap(makePath(iconDirectory, "pencil.png"), (110, 110),
                                                        self.show_list_creator)
        self.list_creator_button.setStyleSheet("background-color: transparent; border: none;")
        self.list_creator_label = QLabel('List Creator')
        self.list_creator_label.setAlignment(Qt.AlignCenter)
        self.list_creator_layout = create_centered_button_layout(self.list_creator_button, self.list_creator_label)
        self.stats_button = create_button_with_pixmap(makePath(iconDirectory, "stats.png"), (110, 110), self.show_stats)
        self.stats_button.setStyleSheet("background-color: transparent; border: none;")
        self.stats_label = QLabel('Stats')
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_layout = create_centered_button_layout(self.stats_button, self.stats_label)
        self.nutrition_button = create_button_with_pixmap(makePath(iconDirectory, "nutrition.png"), (110, 110),
                                                     self.show_nutrition)
        self.nutrition_button.setStyleSheet("background-color: transparent; border: none;")
        self.nutrition_label = QLabel('Nutrition')
        self.nutrition_label.setAlignment(Qt.AlignCenter)
        self.nutrition_layout = create_centered_button_layout(self.nutrition_button, self.nutrition_label)

        # Add the sidebar buttons to the sidebar layout
        if self.window_number==1:
            sidebar_layout.addLayout(self.todolist_layout)
            sidebar_layout.addLayout(self.settings_layout)
            sidebar_layout.addLayout(self.list_creator_layout)
            sidebar_layout.addLayout(self.stats_layout)
            sidebar_layout.addLayout(self.nutrition_layout)

        # Create the central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(label)
        central_layout.setContentsMargins(0, 0, 0, 0)

        # Add the sidebar widget to a QDockWidget
        if self.window_number == 1:
            sidebar_dock = QDockWidget("Sidebar", self)
            sidebar_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
            sidebar_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
            sidebar_dock.setWidget(sidebar_widget)
            sidebar_dock.setTitleBarWidget(QWidget())  # Hide the title bar
            sidebar_dock.setMaximumWidth(200)
            sidebar_dock.setMinimumWidth(0)
            sidebar_dock.setHidden(not self.sidebar_visible)
        if self.window_number == 1:
            self.addDockWidget(Qt.LeftDockWidgetArea, sidebar_dock)


        # Set the central widget
        self.setCentralWidget(central_widget)

        if self.window_number == 1:
            self.show_todolist()
        else:
            self.show_chat()

    def toggle_sidebar_size(self):
        # Toggle the size of the sidebar
        if self.sidebar_visible:
            self.todolist_button.hide()
            self.todolist_label.hide()
            self.settings_button.hide()
            self.settings_label.hide()
            self.list_creator_button.hide()
            self.list_creator_label.hide()
            self.stats_button.hide()
            self.stats_label.hide()
            self.nutrition_button.hide()
            self.nutrition_label.hide()
        else:
            self.todolist_button.show()
            self.todolist_label.show()
            self.settings_button.show()
            self.settings_label.show()
            self.list_creator_button.show()
            self.list_creator_label.show()
            self.stats_button.show()
            self.stats_label.show()
            self.nutrition_button.show()
            self.nutrition_label.show()

        self.sidebar_visible = not self.sidebar_visible

    # Below are the functions for the main window class
    def show_stats(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        stats_window = StatsWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(stats_window)

    def show_nutrition(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        nutrition_window = NutritionWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(nutrition_window)

    def show_todolist(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        todolist_window = TodoListWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        self.setCentralWidget(todolist_window)

    def show_settings(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        settings_window = SettingsWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        self.setCentralWidget(settings_window)

    def show_list_creator(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        list_creator_window = ListCreatorWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(list_creator_window)
    def show_chat(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        chat_window = ChatWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(chat_window)

    def start_scheduling(self):
        self.schedule_thread = ScheduleThread(self.todo_list, self.settings, self)
        self.schedule_thread.start()

    def start_blocking(self):
        self.block_thread = BlockThread(self.block_lists, self)
        self.block_thread.start()

