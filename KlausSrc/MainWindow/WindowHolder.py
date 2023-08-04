from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy, QDesktopWidget, QDockWidget, QSpacerItem

from KlausSrc import ChatWindow, ListCreatorWindow, SettingsWindow, CalendarWindow, NutritionWindow, StatsWindow
from KlausSrc.Utilities.config import iconDirectory, wallpaperDirectory
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from KlausSrc.MainWindow.TodolistWindow import TodoListWindow
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath
from KlausSrc.GlobalModules.GlobalThreads import shared_state, kill_timer_thread2

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QDockWidget, QDesktopWidget, QPushButton
from PyQt5.QtGui import QPixmap, QPalette, QBrush


class WindowHolder(QMainWindow):
    def __init__(self, todo_list_archive, todo_list, block_lists, settings, window1, window2):
        super().__init__()

        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_lists = block_lists
        self.settings = settings
        self.window1 = window1
        self.window2 = window2
        self.sidebar_visible = True  # Added this for sidebar functionality

        # Set the geometry and position of the main windows
        self.window1.setGeometry(0, 0, self.width() // 2, self.height()//2)
        self.window2.setGeometry(self.width() // 2, 0, self.width() // 2, self.height()//2)
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)

        # Create the main layout
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.window_layout = QHBoxLayout()  # Window layout
        self.window_layout.addWidget(self.window1)
        self.window_layout.addWidget(self.window2)

        # Create the sidebar
        self.sidebar_widget = QWidget(self)
        self.sidebar_widget.setStyleSheet("background-color: #cfcfcf;")
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)

        # Add buttons to the sidebar
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

        self.calendar_button = create_button_with_pixmap(makePath(iconDirectory, "calender.png"), (110, 110),
                                                         self.show_calendar)
        self.calendar_button.setStyleSheet("background-color: transparent; border: none;")
        self.calendar_label = QLabel('Calendar')
        self.calendar_label.setAlignment(Qt.AlignCenter)
        self.calendar_layout = create_centered_button_layout(self.calendar_button, self.calendar_label)

        # Add the sidebar to a QDockWidget
        self.sidebar_dock = QDockWidget("Sidebar", self)
        self.sidebar_dock.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.sidebar_dock.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.sidebar_dock.setWidget(self.sidebar_widget)
        self.sidebar_dock.setTitleBarWidget(QWidget())  # Hide the title bar
        self.sidebar_dock.setMaximumWidth(200)
        self.sidebar_dock.setMinimumWidth(0)
        self.sidebar_dock.setHidden(not self.sidebar_visible)

        # Add the QDockWidget to the main window
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sidebar_dock)

        sidebar_widget = QWidget(self)
        sidebar_widget.setStyleSheet("background-color: #cfcfcf;")
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.addLayout(self.todolist_layout)
        sidebar_layout.addLayout(self.settings_layout)
        sidebar_layout.addLayout(self.list_creator_layout)
        sidebar_layout.addLayout(self.stats_layout)
        # sidebar_layout.addLayout(self.nutrition_layout)
        sidebar_layout.addLayout(self.calendar_layout)

        # Continue with main layout
        self.main_layout.addLayout(self.window_layout)
        self.setCentralWidget(self.main_widget)
        self.window1.show()
        self.window2.show()

    def add_sidebar_button(self, image_name, button_name):
        button = QPushButton()
        button.setText(button_name)
        button.setIcon(QIcon(image_name))
        button.setIconSize(QSize(40, 40))  # Set your desired size here.
        button.setFixedSize(200, 50)  # Set your desired button size here.
        self.sidebar_layout.addWidget(self.todolist_layout)


    def set_wallpaper(self, wallpaper_name):
        # Get the size of the window to scale the image
        window_width, window_height = self.width(), self.height()

        # Now, set the background image
        self.setAutoFillBackground(True)
        palette = self.palette()
        wallpaper_path = makePath(wallpaperDirectory, wallpaper_name)

        # Scale the image to fit the window
        pixmap = QPixmap(wallpaper_path).scaled(window_width, window_height, Qt.KeepAspectRatioByExpanding)
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

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

    def show_calendar(self):
        if shared_state.get_timer_thread() is not None:
            kill_timer_thread2(shared_state.get_timer_thread())
        calendar_window = CalendarWindow(self.settings, self.todo_list)
        self.setCentralWidget(calendar_window)

    def show_todolist(self):
        if shared_state.get_timer_thread() is not None:
            print("Finna kill holder")
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