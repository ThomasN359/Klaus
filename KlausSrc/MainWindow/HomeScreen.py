from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QBrush, QPixmap
from PyQt5.QtWidgets import *

from KlausSrc.PopUpWindows.StartTimerPopUp import StartTimerPopUp
from KlausSrc.Objects.Task import TaskType
from KlausSrc.GlobalModules.GlobalThreads import stop_timer_animation, TimerThread
from KlausSrc.MainWindow.CalendarWindow import CalendarWindow
from KlausSrc.MainWindow.StatsWindow import StatsWindow
from KlausSrc.MainWindow.BlockManager import BlockManagerWindow
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
from datetime import *
from KlausSrc.Utilities.config import pickleDirectory
import pickle
from collections import deque
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
    def __init__(self, todo_list_archive, todo_list, block_lists, settings, scheduler, window_number, parent=None):
        super().__init__(parent)
        self.window_number = window_number
        self.scheduler = scheduler
        #self.setStyleSheet("background-color: transparent; border: none;") if you want wallpapers it should be transparent
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_lists = block_lists
        self.settings = settings
        self.setWindowTitle("Klaus")

        if self.window_number == 1:
            self.start_scheduling()
            self.start_blocking()

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
        self.timeStamp = datetime.now().date()


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
        self.block_manager_button = create_button_with_pixmap(makePath(iconDirectory, "pencil.png"), (110, 110),
                                                        self.show_block_manager)
        self.block_manager_button.setStyleSheet("background-color: transparent; border: none;")
        self.block_manager_label = QLabel('List Creator')
        self.block_manager_label.setAlignment(Qt.AlignCenter)
        self.block_manager_layout = create_centered_button_layout(self.block_manager_button, self.block_manager_label)

        self.stats_button = create_button_with_pixmap(makePath(iconDirectory, "stats.png"), (110, 110), self.show_stats)
        self.stats_button.setStyleSheet("background-color: transparent; border: none;")
        self.stats_label = QLabel('Stats')
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_layout = create_centered_button_layout(self.stats_button, self.stats_label)

        self.nutrition_button = create_button_with_pixmap(makePath(iconDirectory, "nutrition.png"), (110, 110), self.show_nutrition)
        self.nutrition_button.setStyleSheet("background-color: transparent; border: none;")
        self.nutrition_label = QLabel('Nutrition')
        self.nutrition_label.setAlignment(Qt.AlignCenter)
        self.nutrition_layout = create_centered_button_layout(self.nutrition_button, self.nutrition_label)

        self.calendar_button = create_button_with_pixmap(makePath(iconDirectory, "calender.png"), (110, 110), self.show_calendar)
        self.calendar_button.setStyleSheet("background-color: transparent; border: none;")
        self.calendar_label = QLabel('Calendar')
        self.calendar_label.setAlignment(Qt.AlignCenter)
        self.calendar_layout = create_centered_button_layout(self.calendar_button, self.calendar_label)

        # Add the sidebar buttons to the sidebar layout
        if self.window_number == 1:
            sidebar_layout.addLayout(self.todolist_layout)
            sidebar_layout.addLayout(self.settings_layout)
            sidebar_layout.addLayout(self.block_manager_layout)
            sidebar_layout.addLayout(self.stats_layout)
            #sidebar_layout.addLayout(self.nutrition_layout)
            sidebar_layout.addLayout(self.calendar_layout)

        # Create the central widget
        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
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
            # Initializes the timer task thread since it's global. But it's not active yet.
            self.timer_thread = TimerThread(None, self)
            shared_state.set_timer_thread(self.timer_thread)
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
            self.block_manager_button.hide()
            self.block_manager_label.hide()
            self.stats_button.hide()
            self.stats_label.hide()
            self.calendar_label.hide()
            self.calendar_button.hide()
        else:
            self.todolist_button.show()
            self.todolist_label.show()
            self.settings_button.show()
            self.settings_label.show()
            self.block_manager_button.show()
            self.block_manager_label.show()
            self.stats_button.show()
            self.stats_label.show()
            self.calendar_label.show()
            self.calendar_button.show()

        self.sidebar_visible = not self.sidebar_visible

    # Below are the functions for the main window class
    def show_stats(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())

        stats_window = StatsWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(stats_window)

    def show_nutrition(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())
        nutrition_window = NutritionWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(nutrition_window)

    def show_calendar(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())
        calendar_window = CalendarWindow(self.settings, self.todo_list)
        self.setCentralWidget(calendar_window)

    def show_todolist(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())
        print("Parent string 2 is " + str(self.timeStamp))
        todolist_window = TodoListWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings, self.timeStamp, self.scheduler)
        self.setCentralWidget(todolist_window)

    def show_settings(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())
        settings_window = SettingsWindow(self.todo_list_archive, self.todo_list, self.block_lists, self.settings)
        self.setCentralWidget(settings_window)

    def show_block_manager(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())
        block_manager_window = BlockManagerWindow(self.todo_list_archive, self.todo_list, self.block_lists)
        self.setCentralWidget(block_manager_window)

    def show_chat(self):
        if shared_state.get_timer_thread() is not None:
            stop_timer_animation(shared_state.get_timer_thread())
        chat_window = ChatWindow(self.todo_list_archive, self.todo_list)
        self.setCentralWidget(chat_window)

    def start_scheduling(self):
        self.schedule_thread = ScheduleThread(self.todo_list, self.settings, self)
        self.schedule_thread.show_popup_signal.connect(self.show_popup)
        self.schedule_thread.start()

    def show_popup(self, task_name):
        for task in self.todo_list:
            if task.task_type == TaskType.TIMER and task.task_name == task_name:
                task.start_by = None

        todoData = {"tasks": self.todo_list, "date": datetime.now().date(), "type": "TODOLIST"}
        with open(pickleDirectory + "todo_list.pickle", "wb") as f:
            pickle.dump(todoData, f)
            f.flush()

        self.start_timer_popup = StartTimerPopUp(task_name)
        self.start_timer_popup.exec_()
        # Once the popup is closed, allow another one to be opened


    def start_blocking(self):
        self.block_thread = BlockThread(self.block_lists, self)
        self.block_thread.start()

