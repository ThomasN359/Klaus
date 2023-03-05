from KlausSrc import *
from Settings import *
from KlausSrc.Task import TaskStatus
from Task import *

import multiprocessing
import random
import sys
from multiprocessing import Value, Lock
import os
import subprocess
import traceback
import pickle
import threading
from datetime import *
from PyQt5 import QtCore
from winotify import Notification, audio
import time
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import *
import pyautogui
import ctypes
import enum

# Global Variables (other clasess import them from here):
parentDirectory = os.path.abspath(os.path.join(os.getcwd(), '..'))
klausDirectory = os.path.join(parentDirectory, 'Klaus')
pickleDirectory = os.path.join(klausDirectory, 'Pickles')
pictureDirectory = os.path.join(klausDirectory, 'Pics')


class QuickListAddWindow(QDialog):
    def __init__(self, parent, todo_list):
        self.todo_list = todo_list
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 500, 300)
        self.setWindowTitle("Quick Add")

        self.layout = QVBoxLayout()

        # Name Your List Label
        self.name_label = QLabel("Name your current list to quick save it")
        self.layout.addWidget(self.name_label)

        # Name Task
        self.name_textbox = QLineEdit()
        self.layout.addWidget(self.name_textbox)

        # Quick Save Button
        self.quick_save_button = QPushButton("Quick Save")
        self.quick_save_button.clicked.connect(self.quick_save)
        self.layout.addWidget(self.quick_save_button)

        self.choose_label = QLabel("Choose a list to quick add")
        self.layout.addWidget(self.choose_label)

        # Display the files from your file directory to display in the drop down "choose" box
        self.choose_combobox = QComboBox()

        for filename in os.listdir(pickleDirectory):
            if filename.endswith("qs.pickle"):
                self.choose_combobox.addItem(filename.replace("qs.pickle", ""))

        self.layout.addWidget(self.choose_combobox)

        # Quick Add
        self.quick_add_button = QPushButton("Quick Add")
        self.quick_add_button.clicked.connect(self.quick_add)
        self.layout.addWidget(self.quick_add_button)

        self.setLayout(self.layout)

    # This function connects to the Quick Save button and quick saves by dumping it into a file on your computer
    def quick_save(self):
        pickle_file = pickleDirectory + "/" + self.name_textbox.text() + "qs.pickle"
        if not os.path.exists(pickleDirectory):
            os.makedirs(pickleDirectory)

        data = ("Quick Add", self.todo_list)

        with open(pickle_file, "wb") as f:
            pickle.dump(data, f)

    # This function connects to the quick add button
    def quick_add(self):
        chosen_pickle = "Pickles/" + self.choose_combobox.currentText() + "qs.pickle"
        with open(chosen_pickle, "rb") as f:
            data = pickle.load(f)
        self.todo_list.extend(data[1])
        self.parent().initUI()
        self.close()
        self.parent().repaint()
        self.parent().update()


class AddTaskWindow(QDialog):
    # index denotes the hbox index for the task line widget
    def __init__(self, parent, todo_list_archive, todo_list, block_list, settings, index):
        self.todo_list = todo_list
        self.settings = settings
        self.todo_list_archive = todo_list_archive
        super().__init__(parent)
        self.reminders = []
        self.index = index
        self.block_list = block_list
        self.has_daily_block = False
        if len(self.block_list[0][0]) != 0:
            self.has_daily_block = True
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 500, 500)
        currTask = None

        # If we have == ADD_TASK that means we're launching this from "Add Task" and not "Edit Task"
        self.ADD_TASK = -1
        if self.index == self.ADD_TASK:
            self.setWindowTitle("Add Task")
        else:
            self.setWindowTitle("Edit Task")
            currTask = self.todo_list[self.index]

        layout = QVBoxLayout()

        self.error_label = QLabel("Timer Task Require a Duration ")
        self.error_label.setStyleSheet("color: red")
        self.error_label.hide()
        layout.addWidget(self.error_label)

        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()

        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        if self.index != self.ADD_TASK:
            self.name_edit.setText(currTask.task_name)

        description_label = QLabel("Description:")
        self.description_edit = QTextEdit()

        if self.index != self.ADD_TASK:
            self.description_edit.setText(currTask.task_description)

        layout.addWidget(description_label)
        layout.addWidget(self.description_edit)

        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("Active")
        self.type_combo.addItem("Timer")
        self.type_combo.addItem("Sustain")
        self.type_combo.addItem("BedTime")

        if self.index != self.ADD_TASK:
            if currTask.task_type == TaskType.TIMER:
                self.type_combo.setCurrentIndex(1)  # set combo box to Timer
            elif currTask.task_type == TaskType.SUSTAIN:
                self.type_combo.setCurrentIndex(2)
            elif currTask.task_type == TaskType.BEDTIME:
                self.type_combo.setCurrentIndex(3)

        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        reminder_label = QLabel("Reminder:")
        self.reminder_edit = QTimeEdit()

        self.add_reminder_button = QPushButton("Add a Reminder")
        if self.index != -1 and currTask.task_type != TaskType.SUSTAIN:
            self.reminders = currTask.reminder
        self.add_reminder_button.clicked.connect(self.add_to_reminders)

        layout.addWidget(reminder_label)
        layout.addWidget(self.reminder_edit)
        layout.addWidget(self.add_reminder_button)

        due_by_label = QLabel("Due by:")
        self.due_by_edit = QTimeEdit()
        default_time = self.settings.daily_start_time
        self.due_by_edit.setTime(default_time)

        # IF there exist a bedtime, then use it
        for task in self.todo_list:
            if task.task_type == TaskType.BEDTIME:
                default_time = task.due_by
                suffix = default_time[-2:].upper()
                hour, minute = default_time[:-3].split(":")
                hour = int(hour)
                if suffix == "PM" and hour < 12:
                    hour += 12
                elif suffix == "AM" and hour == 12:
                    hour = 0
                time_str_24h = f"{hour:02d}:{minute}"
                # Convert the 24-hour time format string to a QTime object
                qtime = QTime.fromString(time_str_24h, "HH:mm")
                self.due_by_edit.setTime(qtime)
                # TODO make a global helper function that converts time

        if self.index != self.ADD_TASK:
            default_time = currTask.due_by
            # Convert QTime object to a 24-hour time format string
            # Convert the time string to a 24-hour time format string
            suffix = default_time[-2:].upper()
            hour, minute = default_time[:-3].split(":")
            hour = int(hour)
            if suffix == "PM" and hour < 12:
                hour += 12
            elif suffix == "AM" and hour == 12:
                hour = 0
            time_str_24h = f"{hour:02d}:{minute}"

            # Convert the 24-hour time format string to a QTime object
            qtime = QTime.fromString(time_str_24h, "HH:mm")
            self.due_by_edit.setTime(qtime)

        layout.addWidget(due_by_label)
        layout.addWidget(self.due_by_edit)
        if self.index != self.ADD_TASK:
            if (currTask.task_type == TaskType.ACTIVE
                    or currTask.task_type == TaskType.TIMER
                    or currTask.task_type == TaskType.BEDTIME):
                dt = datetime.strptime(currTask.due_by, "%I:%M %p")
                time = QTime(dt.hour, dt.minute, dt.second)
                self.due_by_edit.setTime(time)
        self.duration_label = QLabel("Duration:")
        self.duration_edit = QLineEdit()
        self.duration_label.hide()
        self.duration_edit.hide()
        if self.index != self.ADD_TASK and currTask.task_type == TaskType.TIMER:
            self.duration_edit.setText(str(currTask.duration // 60))
        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_edit)

        self.app_block_list_label = QLabel("App Block List:")
        self.app_block_list_combo = QComboBox()
        self.app_block_list_combo.addItem("None")

        for filename in os.listdir(pickleDirectory):
            if filename.endswith("APPLIST.pickle"):
                self.app_block_list_combo.addItem(filename)

        self.app_block_list_label.hide()
        self.app_block_list_combo.hide()

        self.web_block_list_label = QLabel("Web Block List:")
        self.web_block_list_combo = QComboBox()
        self.web_block_list_combo.addItem("None")

        for filename in os.listdir(pickleDirectory):
            if filename.endswith("WEBLIST.pickle"):
                self.web_block_list_combo.addItem(filename)

        self.web_block_list_label.hide()
        self.web_block_list_combo.hide()

        layout.addWidget(self.app_block_list_label)
        layout.addWidget(self.app_block_list_combo)
        layout.addWidget(self.web_block_list_label)
        layout.addWidget(self.web_block_list_combo)

        self.enable_shutdown_checkbox = QCheckBox("Enable Shutdown")
        self.enable_shutdown_checkbox.setCheckState(Qt.Unchecked)
        layout.addWidget(self.enable_shutdown_checkbox)
        self.enable_shutdown_checkbox.hide()

        if self.index == self.ADD_TASK:
            self.save = QPushButton("Add Task")
        else:
            self.save = QPushButton("Save Edit")

        self.save.clicked.connect(self.add_task)
        layout.addWidget(self.save)
        self.setLayout(layout)

        self.type_combo.currentIndexChanged.connect(self.show_task_type)
        self.show_task_type()

    # Below are the functions for the add list class
    def add_to_reminders(self):
        self.reminders.append(self.reminder_edit.text())

    def add_task(self):
        name = self.name_edit.text()
        description = self.description_edit.toPlainText()
        task_type = self.type_combo.currentText()

        # Error means user tried to hit add/save task without filling all required boxes
        error = False

        # The drop down menu for add task will cause the add task dialouge box to change based off of the task type
        if task_type == "Active":
            due_by = self.due_by_edit.text()
            task = ActiveTask(name, description, TaskStatus.PENDING, self.reminders, due_by)
        elif task_type == "Timer":
            due_by = self.due_by_edit.text()
            if self.duration_edit.text() == "":
                self.error_label.show()
                error = True
            else:
                duration = int(self.duration_edit.text()) * 60
                app_block_list = self.app_block_list_combo.currentText()
                web_block_list = self.web_block_list_combo.currentText()
                task = TimerTask(name, description, TaskStatus.PENDING, self.reminders, due_by, duration,
                                 app_block_list, web_block_list)
        elif task_type == "Sustain":
            contract = description
            end_time = self.due_by_edit.text()
            task = SustainTask(name, description, TaskStatus.PENDING, contract, end_time)
        elif task_type == "BedTime":
            shutdown = True
            due_by = self.due_by_edit.text()
            task = BedTime(name, description, TaskStatus.PENDING, due_by, self.reminders, shutdown)
        if not error:
            self.has_daily_block = False
            self.block_list[0][0] = []

            if self.index == self.ADD_TASK:
                self.todo_list.append(task)
            else:
                self.todo_list[self.index] = task
            self.reminders = []
            self.parent().initUI()
            self.close()
            self.parent().repaint()
            self.parent().update()
            # Saving the task list to a file
            todoData = {"Tasks": self.todo_list, "Date": datetime.now().date()}
            with open(pickleDirectory + "todo_list.pickle", "wb") as f:
                pickle.dump(todoData, f)
                f.flush()

    def show_task_type(self):
        task_type = self.type_combo.currentText()
        if task_type == "Timer":
            self.duration_label.show()
            self.duration_edit.show()
            self.app_block_list_label.show()
            self.app_block_list_combo.show()
            self.web_block_list_label.show()
            self.web_block_list_combo.show()

        elif task_type == "BedTime":
            self.enable_shutdown_checkbox.show()
        else:
            self.duration_label.hide()
            self.duration_edit.hide()
            self.app_block_list_label.hide()
            self.app_block_list_combo.hide()
            self.web_block_list_label.hide()
            self.web_block_list_combo.hide()
            self.enable_shutdown_checkbox.hide()


class ListCreatorWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.initUI()

    def initUI(self):
        label = QLabel("List Creator", self)
        label.setAlignment(Qt.AlignCenter)

        list_name_label = QLabel("List Name:", self)
        self.list_name_textbox = QLineEdit(self)

        list_type_label = QLabel("List Type:", self)
        self.list_type_combobox = QComboBox(self)
        self.list_type_combobox.addItems(["Block Apps", "Block Websites"])

        list_entries_label = QLabel("List Entries:", self)
        self.list_entries_textbox = QTextEdit(self)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_list)
        back_button = QPushButton("Back", self)
        back_button.clicked.connect(self.go_back)

        edit_list_label = QLabel("Edit a List:", self)
        self.edit_list_combobox = QComboBox(self)
        self.edit_list_combobox.addItems(["None", "Example List 1", "Example List 2", "Example List 3"])
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_name)
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_content)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(back_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addWidget(list_name_label)
        main_layout.addWidget(self.list_name_textbox)
        main_layout.addWidget(edit_list_label)
        main_layout.addWidget(self.edit_list_combobox)
        main_layout.addWidget(list_type_label)
        main_layout.addWidget(self.list_type_combobox)
        main_layout.addWidget(list_entries_label)
        main_layout.addWidget(self.list_entries_textbox)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def update_list_name(self, list_name):
        self.list_name_textbox.setText(list_name)

    def update_list_content(self, list_name):
        try:
            with open(f"{list_name}.pickle", "rb") as f:
                data = pickle.load(f)
                self.list_entries_textbox.setPlainText(" ".join(data["entries"]))
                self.list_type_combobox.setCurrentText(data["status"])
        except FileNotFoundError:
            self.list_entries_textbox.setPlainText("")
            self.list_type_combobox.setCurrentText("")

    def save_list(self):
        list_name = self.list_name_textbox.text()
        list_type = self.list_type_combobox.currentText()
        if (list_type == "Block Apps"):
            list_name = list_name + "APPLIST"
        else:
            list_name = list_name + "WEBLIST"
        list_entries = self.list_entries_textbox.toPlainText()
        entries = list_entries.split(" ")

        data = {
            "status": "INACTIVE",
            "entries": entries
        }

        with open(f"{pickleDirectory}/{list_name}.pickle", "wb") as f:
            pickle.dump(data, f)
            f.flush()

    def go_back(self):
        self.parent().initUI()


class StatsWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Create a QLabel widget and set its text
        label = QLabel(self)
        label.setText("This is the User Stats window")
        label.setAlignment(Qt.AlignCenter)

        # Create a layout for the buttons
        buttons_layout = QHBoxLayout()

        # Create the "Back" button and connect it to the "go_back" slot
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        buttons_layout.addWidget(self.back_button)

        # Add the buttons layout to the main layout of the widget
        main_layout = QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def go_back(self):
        self.parent().initUI()


class NutritionWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 100, 100)
        self.initUI()

    def initUI(self):
        # Initialize variables
        self.daily_metabolic_rate = 0
        self.net_calories = 0
        self.last_save_time = datetime.now()

        # Load saved data from pickle
        try:
            with open(pickleDirectory + "/net_calories.pickle", "rb") as f:
                self.last_save_time, self.net_calories, self.daily_metabolic_rate = pickle.load(f)
        except FileNotFoundError:
            pass

        # Create GUI elements
        self.net_calories_label = QLabel("Net Calories: 0")
        self.add_calories_button = QPushButton("Add Calories")
        self.calories_input = QLineEdit()
        self.metabolic_rate_input = QLineEdit()
        self.metabolic_rate_input.setText(str(self.daily_metabolic_rate))
        self.net_pounds_label = QLabel("Net Pounds: 0")
        # Create the "Back" button and connect it to the "go_back" slot
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)

        # Connect button click event to add_calories method
        self.add_calories_button.clicked.connect(self.on_add_calories_clicked)

        # Create timer to update net calories every second
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_net_calories)
        self.timer.start(1000)  # 1000 ms = 1 second

        # Add GUI elements to layout
        layout = QVBoxLayout()
        layout.addWidget(self.net_calories_label)
        layout.addWidget(self.net_pounds_label)
        layout.addWidget(self.calories_input)
        layout.addWidget(self.add_calories_button)
        layout.addWidget(QLabel("Daily Metabolic Rate:"))
        layout.addWidget(self.metabolic_rate_input)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def update_net_calories(self):
        # Calculate time elapsed since last update
        now = datetime.now()
        time_elapsed = (now - self.last_save_time).total_seconds()
        self.last_save_time = now

        # Calculate net calories
        net_calories_lost = self.daily_metabolic_rate / 86400  # 86400 seconds in a day
        self.net_calories -= net_calories_lost * time_elapsed

        # Save net calories and metabolic rate to pickle every minute
        if now.second % 12 == 0:
            with open(pickleDirectory + "/net_calories.pickle", "wb") as f:
                pickle.dump((now, self.net_calories, self.daily_metabolic_rate), f)

        # Calculate net pounds and format as decimal with 4 digits
        net_pounds = self.net_calories / 3500
        net_pounds_formatted = "{:.6f}".format(net_pounds)

        # Format net calories as decimal with 4 digits and update net calories and net pounds labels
        net_calories_formatted = "{:.4f}".format(self.net_calories)
        self.net_calories_label.setText("Net Calories: {}".format(net_calories_formatted))
        self.net_pounds_label.setText("Net Pounds: {}".format(net_pounds_formatted))

    def on_add_calories_clicked(self):
        # Get calories input value and add to net calories
        calories = int(self.calories_input.text())
        self.net_calories += calories

        # Update net calories and net pounds labels
        net_calories_formatted = "{:.4f}".format(self.net_calories)
        self.net_calories_label.setText("Net Calories: {}".format(net_calories_formatted))
        net_pounds = self.net_calories / 3500
        net_pounds_formatted = "{:.4f}".format(net_pounds)
        self.net_pounds_label.setText("Net Pounds: {}".format(net_pounds_formatted))

    def update_metabolic_rate(self, metabolic_rate):
        self.daily_metabolic_rate = metabolic_rate
        self.metabolic_rate_input.setText(str(metabolic_rate))

    def save_stats(self):
        # Save net calories and metabolic rate to pickle
        now = datetime.datetime.now()
        with open(pickleDirectory + "/net_calories.pickle", "wb") as f:
            pickle.dump((now, self.net_calories, self.daily_metabolic_rate), f)

    def load_stats(self):
        # Load saved data from pickle
        try:
            with open(pickleDirectory + "/net_calories.pickle", "rb") as f:
                self.last_save_time, self.net_calories, self.daily_metabolic_rate = pickle.load(f)
        except FileNotFoundError:
            pass

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            metabolic_rate = int(self.metabolic_rate_input.text())
            self.update_metabolic_rate(metabolic_rate)
        else:
            super().keyPressEvent(event)

    def go_back(self):
        self.parent().initUI()


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


def main_process():  # TODO FLAG AND LOCK

    # Initialize the starting variabels for the program
    settings = Settings()
    todo_list = []
    todo_list_archive = []
    block_lists = [[[], [], [], ], [[], [], []]]
    timeStamp = None

    # Below here, items are loaded and initialized in your system, such as settings, todolist, block list etc.
    # Load in saved block list if they exist


    for filename in os.listdir(pickleDirectory):
        filename = "Pickles/" + filename
        if filename.endswith("APPLIST.pickle"):
            try:
                with open(filename, "rb") as f:
                    blockData = pickle.load(f)
                    blockStatus = blockData["status"]
                    blockEntries = blockData["entries"]
                    if blockStatus == "DAILY":
                        block_lists[0][0] = blockEntries
                    elif blockStatus == "GENERAL":
                        block_lists[0][1] = blockEntries
                    elif blockStatus == "TIMER":
                        blockData["status"] = "INACTIVE"
                        blockStatus = "INACTIVE"
                        with open(filename, "wb") as f:
                            pickle.dump(blockData, f)
            except Exception as e:
                print(e)

    # Load in t0dolist archive
    try:
        with open(pictureDirectory + "/todo_list_archive.pickle", "rb") as f:
            todo_list_archive = pickle.load(f)
    except:
        # Handle the exception and continue without the data
        todo_list_archive = []
        pass

    # Load in most recent t0do list
    try:
        with open(pickleDirectory + "/todo_list.pickle", "rb") as f:
            todoData = pickle.load(f)
            todo_list = todoData["Tasks"]
            timeStamp = todoData["Date"]
    except:
        # Handle the exception and continue without the data
        todo_list = []
        pass

    # Load in settings
    try:
        with open(pickleDirectory + "/settings.pickle", "rb") as f:
            settings = pickle.load(f)
    except:
        # Handle the exception and continue without the data
        settings.daily_start_time = QTime(0, 0)
        settings.enable_lock_out = False
        # First is Brave, second is Chrome, Third is edge. These check which browsers you currently use.
        settings.browsers = [False, True, False]
        settings.klaus_state = KlausFeeling.HAPPY
        settings.enable_dialogue_reminder_window = True

    # The below if code block is responsible for blocking your internet use if you haven't made a todolist today
    if (datetime.now().hour >= settings.daily_start_time.hour() and (
            datetime.now().date() != timeStamp or timeStamp is None) and settings.enable_lock_out):
        if len(todo_list) > 0:
            todo_list_archive.append({timeStamp: todo_list})  # if there was a previous todolist archive it
            try:
                with open(pickleDirectory + "/todo_list_archive.pickle", "wb") as f:
                    pickle.dump(todo_list_archive, f)
                    f.flush()
            except:
                # Handle the exception and continue without the data
                print("Error loading archive pickle")
                pass
        blockedApps = []
        if settings.browsers[0]:
            blockedApps.append("brave.exe")
        if settings.browsers[1]:
            blockedApps.append("chrome.exe")
        if settings.browsers[2]:
            blockedApps.append("msedge.exe")
        block_lists[0][0] = blockedApps
        todo_list = []  # refresh the todolist because it's a new day

    app = QApplication([])
    font = QFont("Arial", 15)
    app.setFont(font)
    main_window = HomeScreen(todo_list_archive, todo_list, block_lists, settings)
    main_window.show()
    # This handles the schedule things such as notifications
    main_window.start_scheduling()
    main_window.start_blocking()
    # Connect close event to handle_close_event
    # main_window.closeEvent = lambda event: handle_close_event(event, flag, lock) TODO flag and lock
    # This handles the block list
    app.exec()


def main():
    # Create GUI process
    # event = multiprocessing.Event()
    # lock = multiprocessing.Lock()
    # flag = multiprocessing.Value('i', 1)
    #
    # gui_klaus = multiprocessing.Process(target=main_process, args=(flag, lock))
    # gui_klaus.start()
    #
    # # Wait for GUI to start
    # time.sleep(1)
    #
    # # Create checker process
    # checker_p = multiprocessing.Process(target=checker_process, args=(flag, lock))
    # checker_p.start()
    #
    # # Wait for GUI process to finish
    # gui_klaus.join()
    # main_process(flag, lock)
    main_process()


# This is a global function that overrides the normal "X" close button by including the information about respawning
def handle_close_event(flag, lock):
    print("Entered here")
    with lock:
        flag.value = 0


def checker_process(flag, lock):
    while True:
        with lock:
            if flag.value == 1:
                pass
                ("GUI is running" + str(flag.value))
            else:
                print("GUI is closed with value " + str(flag.value))
                # Start a new GUI process if the previous one was closed
                new_gui_p = multiprocessing.Process(target=main_process, args=(flag, lock))
                flag.value = 1
                new_gui_p.start()
        time.sleep(1)


# This is where the web browser block list is handled
def automate_browser(block_lists, settings):
    try:
        # create the mega block list by combining all the current lists
        fullList = block_lists[1][0] + block_lists[1][1]
        block_str = '\n'.join(fullList) + '\n'

        # Get screen DPI
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        screen_dpi = user32.GetDpiForSystem()

        # Calculate zoom factor
        zoom_factor = screen_dpi / 96

        # Calculate click coordinates
        x = int(screen_width * 0.3 * zoom_factor)
        y = int(screen_height * 0.3 * zoom_factor)

        # Perform the task for these optional browsers
        # TODO remove i==1 with the users browsers from settings
        for i in range(1, 4):
            if i == 1 and settings.browsers[i - 1] == True:
                browser_exe = 'brave.exe'
                browser_name = 'Brave'
            elif i == 2 and settings.browsers[i - 1] == True:
                browser_exe = 'chrome.exe'
                browser_name = 'Google Chrome'
            elif i == 3 and settings.browsers[i - 1] == True:
                browser_exe = 'msedge.exe'
                browser_name = 'Microsoft\u200b Edge'
            else:
                continue

            # Launch browser
            pyautogui.hotkey('win', 'r')
            pyautogui.typewrite(browser_exe)
            pyautogui.press('enter')

            # Wait for browser to open
            time.sleep(1)

            # Check if browser is maximized
            try:
                win = pyautogui.getWindowsWithTitle(browser_name)[0]
                is_maximized = win.isMaximized

                # Maximize browser window if it's not already maximized
                if not is_maximized:
                    pyautogui.hotkey('win', 'up')
                    # Wait for browser to maximize
                    time.sleep(.05)

                # Navigate to extension URL
                pyautogui.hotkey('ctrl', 'l')
                pyautogui.typewrite('chrome-extension://akfbkbiialncppkngofjpglbbobjoeoe/options.html')
                pyautogui.press('enter')

                # Wait for extension to load
                time.sleep(.7)

                # Click the textbox
                pyautogui.click(x, 2 * y)
                time.sleep(.05)

                # Select all text in textbox
                pyautogui.hotkey('ctrl', 'a')

                # Delete all text in textbox
                pyautogui.press('backspace')

                # Type in block list
                pyautogui.typewrite(block_str)

                # Wait for text to be typed in
                time.sleep(.1)

                # Click the Save button
                pyautogui.click(x / 1.3, 2.4 * y)
                time.sleep(.05)

                # Close the browser
                pyautogui.hotkey('alt', 'f4')
            except IndexError:
                print(f"Unable to find window for {browser_name}")
                continue

    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"Web Blocking Automation Failed: {e}\n\n{tb}"
        print(error_message)


# Decrements the brightness by 1
def decrement_brightness():
    # Get the current brightness level
    completed = subprocess.run(
        ["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
        capture_output=True, text=True)
    current_brightness = int(completed.stdout.strip())

    # Decrement the brightness level by 1
    if current_brightness > 0:
        new_brightness = current_brightness - 1
        command = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1," + str(
            new_brightness) + ")"
        subprocess.run(["powershell", "-Command", command], capture_output=True)
        print(f"Brightness level set to {new_brightness}")
    else:
        print("Cannot decrement brightness level as it is already 0.")


if __name__ == '__main__':
    main()
