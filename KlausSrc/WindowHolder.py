from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy, QDesktopWidget
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt

from KlausSrc.MainWindow.TodolistWindow import TodoListWindow
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath
from KlausSrc.Utilities.config import iconDirectory, wallpaperDirectory
from KlausSrc.MainWindow.HomeScreen import HomeScreen, create_centered_button_layout
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt

from KlausSrc.MainWindow.TodolistWindow import TodoListWindow
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath
from KlausSrc.Utilities.config import iconDirectory
from KlausSrc.MainWindow.HomeScreen import HomeScreen, create_centered_button_layout

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt

from KlausSrc.MainWindow.TodolistWindow import TodoListWindow
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath
from KlausSrc.Utilities.config import iconDirectory
from KlausSrc.MainWindow.HomeScreen import HomeScreen, create_centered_button_layout

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #cfcfcf;")
        self.layout = QVBoxLayout(self)
        self.expand_button = QPushButton("≡")
        self.expand_button.setFixedSize(30, 30)
        self.expand_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.layout.addWidget(self.expand_button)

    def add_button(self, button_layout):
        self.layout.addLayout(button_layout)


class WindowHolder(QMainWindow):
    def __init__(self, todo_list_archive, todo_list, block_lists, settings, window1, window2):
        super().__init__()
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_lists = block_lists
        self.settings = settings
        self.setWindowTitle("Window Holder")
        self.window1 = window1
        self.window2 = window2

        # Set the geometry and position of the main windows
        self.window1.setGeometry(0, 0, self.width() // 2, self.height())
        self.window2.setGeometry(self.width() // 2, 0, self.width() // 2, self.height())

        # Create Menu Bar
        self.menu_bar = self.menuBar()
        self.view_menu = self.menu_bar.addMenu('Screen Type')

        # Create "Single Screen" and "Split Screen" actions
    #    self.single_screen_action = QAction("Single Screen", self)
    #    self.split_screen_action = QAction("Split Screen", self)

        # Add actions to "View" menu
     #   self.view_menu.addAction(self.single_screen_action)
     #   self.view_menu.addAction(self.split_screen_action)

        # Create the main layout
        self.main_widget = QWidget(self)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.window_layout = QHBoxLayout()  # Window layout
        self.window_layout.addWidget(self.window1)
        self.window_layout.addWidget(self.window2)
        self.main_layout.addLayout(self.window_layout)

        self.setCentralWidget(self.main_widget)
        self.window1.show()
        self.window2.show()
        self.set_wallpaper("snow_mountain_2d")

    def set_wallpaper(self, wallpaper_name):
        # First, get the screen resolution to scale the image
        screen = QDesktopWidget().screenGeometry()
        screen_width, screen_height = screen.width(), screen.height()

        # Now, set the background image
        self.setAutoFillBackground(True)
        palette = self.palette()
        wallpaper_path = makePath(wallpaperDirectory, wallpaper_name)

        # Scaling the image to fit the screen
        pixmap = QPixmap(wallpaper_path).scaled(screen_width, screen_height, Qt.KeepAspectRatioByExpanding)
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)

    def toggle_sidebar_size(self):
        # Toggle the size of the sidebar widget
        self.sidebar_widget.setHidden(not self.sidebar_widget.isHidden())

    def show_todolist(self):
        todolist_window = TodoListWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        todolist_window.show()



