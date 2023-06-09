from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy, QDesktopWidget
from KlausSrc.Utilities.config import iconDirectory, wallpaperDirectory
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFrame, QToolBar, \
    QPushButton, QSizePolicy
from PyQt5.QtGui import QPalette, QColor, QBrush, QPixmap
from PyQt5.QtCore import Qt
from KlausSrc.MainWindow.TodolistWindow import TodoListWindow
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath


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
        self.window1.setGeometry(0, 0, self.width() // 2, self.height()//2)
        self.window2.setGeometry(self.width() // 2, 0, self.width() // 2, self.height()//2)
        screen = QDesktopWidget().screenGeometry()
        self.setGeometry(screen)

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
        #self.set_wallpaper("foggy_island.png")

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


    def show_todolist(self):
        todolist_window = TodoListWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        todolist_window.show()



