import subprocess
import pickle
import threading
from datetime import *
from PyQt5 import QtCore
from winotify import Notification, audio
import time
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap
from PyQt5.QtWidgets import *
import socket

import enum
class TaskType(enum.Enum):
    ACTIVE = 1
    TIMER = 2
    SUSTAIN = 3
    BEDTIME = 4
class TaskStatus(enum.Enum):
    PENDING = 1
    PASSED = 2
    FAILED = 3
    PLAYING = 4
class Task:
    def __init__(self, task_name: str, task_description: str, task_type: TaskType, task_status: TaskStatus):
        self.task_name = task_name
        self.task_description = task_description
        self.task_type = task_type
        self.task_status = task_status

    def display_task_name(self):
        print(f"Task Name: {self.task_name}")
        print(f"Task Description: {self.task_description}")
        print(f"Task Type: {self.task_type.name}")

class ActiveTask(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, reminder: list[str], due_by: time):
        super().__init__(task_name, task_description, TaskType.ACTIVE, TaskStatus.PENDING)
        self.reminder = reminder
        self.due_by = due_by

class TimerTask(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, reminder: list[str], due_by: time, duration: int, block_list: str):
        super().__init__(task_name, task_description, TaskType.TIMER, TaskStatus.PENDING)
        self.duration = duration
        self.block_list = block_list
        self.reminder = reminder
        self.due_by = due_by

class SustainTask(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, contract: str, endTime: time):
        super().__init__(task_name, task_description,TaskType.SUSTAIN, TaskStatus.PENDING)
        self.contract = contract
        self.endTime = endTime

class BedTime(Task):
    def __init__(self, task_name: str, task_description: str, task_status: TaskStatus, bed_time: time, reminder: list[str], shutdown: bool):
        super().__init__(task_name, task_description,TaskType.BEDTIME, TaskStatus.PENDING)
        self.bed_time = bed_time
        self.reminder = reminder
        self.shutdown = shutdown

class TimerThread(QThread):
    timer_signal = pyqtSignal(int)
    paused = False

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task

    def run(self):
        time_remaining = int(self.task.duration)
        while time_remaining > 0:
            if self.paused:
                time.sleep(1)  # sleep for 1 second
                continue
            self.timer_signal.emit(time_remaining)
            time.sleep(1)  # sleep for 1 second
            time_remaining -= 1
        self.task.duration = 0
        self.timer_signal.emit(0)
class TodoListWindow(QWidget):
    def __init__(self, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list = todo_list
        self.task_labels = []
        self.check_buttons = []
        self.x_buttons = []
        self.play_buttons = []
        self.cancel_buttons = []
        self.minutes_remaining = []

        self.layout = QVBoxLayout()
        label = QLabel(self)
        label.setText(f"{datetime.now().strftime('%Y-%m-%d')} Todo List")
        font = label.font()
        font.setPointSize(20)
        label.setFont(font)
        label.setAlignment(Qt.AlignHCenter)
        hbox2 = QHBoxLayout()
        self.layout.addWidget(label)
        self.initUI()
        self.setLayout(self.layout)
    def initUI(self):
        widgets = [self.task_labels, self.check_buttons, self.x_buttons, self.play_buttons, self.cancel_buttons,
                   self.minutes_remaining]
        for widget_list in widgets:
            for widget in widget_list:
                if widget is not None:
                    self.layout.removeWidget(widget)
                    widget.deleteLater()
            widget_list.clear()

        for task in self.todo_list:
            if task.task_type == TaskType.ACTIVE:
                hbox = QHBoxLayout()
                task_label = QLabel(task.task_name + "(" + task.due_by + ")", self)
                if (task.task_status == TaskStatus.FAILED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: red")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                elif(task.task_status == TaskStatus.PASSED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: green")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                hbox.addWidget(task_label)
                check_button = QPushButton("\u2713", self)
                check_button.setStyleSheet("background-color: green")
                check_button.setFixedWidth(35)
                check_button.clicked.connect(self.handle_check_click)
                hbox.addWidget(check_button)
                cancel_button = QPushButton("⨺", self)
                cancel_button.setStyleSheet("background-color: yellow")
                cancel_button.setFixedWidth(35)
                hbox.addWidget(cancel_button)
                x_button = QPushButton("\u2715", self)
                x_button.setStyleSheet("background-color: red")
                x_button.setFixedWidth(35)
                x_button.clicked.connect(self.handle_x_click)
                hbox.addWidget(x_button)
                self.layout.addLayout(hbox)
                self.task_labels.append(task_label)
                self.check_buttons.append(check_button)
                self.cancel_buttons.append(cancel_button)
                self.x_buttons.append(x_button)
                self.minutes_remaining.append(None)
                self.play_buttons.append(None)
                cancel_button.clicked.connect(self.handle_cancel_button)
            elif task.task_type == TaskType.TIMER:
                hbox = QHBoxLayout()
                task_label = QLabel(task.task_name + "(" + task.due_by + ")", self)
                if (task.task_status == TaskStatus.FAILED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: red")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                elif(task.task_status == TaskStatus.PASSED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: green")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                hbox.addWidget(task_label)

                hbox.addStretch()
                minutesRemaining = QLabel("Seconds Remaining: {}".format(str(task.duration)))
                hbox.addWidget(minutesRemaining)

                play_button = QPushButton("\u25B6", self)
                play_button.setStyleSheet("background-color: green")
                play_button.setFixedWidth(65)
                play_button.clicked.connect(self.handle_play_click)
                hbox.addWidget(play_button)
                cancel_button = QPushButton("⨺", self)
                cancel_button.setStyleSheet("background-color: yellow")
                cancel_button.setFixedWidth(35)
                hbox.addWidget(cancel_button)
                x_button = QPushButton("\u2715", self)
                x_button.setStyleSheet("background-color: red")
                x_button.setFixedWidth(35)
                x_button.clicked.connect(self.handle_x_click)
                hbox.addWidget(x_button)
                self.layout.addLayout(hbox)
                self.task_labels.append(task_label)
                self.play_buttons.append(play_button)
                self.x_buttons.append(x_button)
                self.cancel_buttons.append(cancel_button)
                self.check_buttons.append(None)
                self.minutes_remaining.append(minutesRemaining)
                cancel_button.clicked.connect(self.handle_cancel_button)
            elif task.task_type == TaskType.SUSTAIN:
                hbox = QHBoxLayout()
                task_label = QLabel(task.task_name + "(" + task.endTime + ")", self)
                if (task.task_status == TaskStatus.FAILED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: red")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                elif(task.task_status == TaskStatus.PASSED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: green")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                hbox.addWidget(task_label)
                hbox.addStretch()
                # current_time = datetime.now()
                # target_time = datetime.combine(current_time.date(), time(23, 59))
                # if target_time < current_time:
                #     target_time += timedelta(days=1)
                # time_difference = target_time - current_time
                # minutes_difference = int(time_difference.total_seconds() / 60)
                minutesRemaining = QLabel("Minutes Remaining: {}".format(str(553)))
                hbox.addWidget(minutesRemaining)
                cancel_button = QPushButton("⨺", self)
                cancel_button.setStyleSheet("background-color: yellow")
                cancel_button.setFixedWidth(35)
                hbox.addWidget(cancel_button)
                x_button = QPushButton("\u2715", self)
                x_button.setStyleSheet("background-color: red")
                x_button.setFixedWidth(35)
                x_button.clicked.connect(self.handle_x_click)
                hbox.addWidget(x_button)
                self.layout.addLayout(hbox)
                self.task_labels.append(task_label)
                self.x_buttons.append(x_button)
                self.check_buttons.append(None)
                self.play_buttons.append(None)
                self.cancel_buttons.append(cancel_button)
                self.minutes_remaining.append(minutesRemaining)
                cancel_button.clicked.connect(self.handle_cancel_button)
            elif task.task_type == TaskType.BEDTIME:
                hbox = QHBoxLayout()
                task_label = QLabel(task.task_name + "(" + task.bed_time + ")", self)
                if (task.task_status == TaskStatus.FAILED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: red")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                elif(task.task_status == TaskStatus.PASSED):
                    task_label.setText("<s>" + task_label.text() + "</s>")
                    task_label.setStyleSheet("color: green")
                    task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
                hbox.addWidget(task_label)
                cancel_button = QPushButton("⨺", self)
                cancel_button.setStyleSheet("background-color: yellow")
                cancel_button.setFixedWidth(35)
                hbox.addWidget(cancel_button)
                x_button = QPushButton("\u2715", self)
                x_button.setStyleSheet("background-color: blue")
                x_button.setFixedWidth(35)
                x_button.clicked.connect(self.handle_x_click)
                hbox.addWidget(x_button)
                self.layout.addLayout(hbox)
                self.task_labels.append(task_label)
                self.x_buttons.append(x_button)
                self.cancel_buttons.append(cancel_button)
                self.check_buttons.append(None)
                self.play_buttons.append(None)
                self.minutes_remaining.append(None)
                cancel_button.clicked.connect(self.handle_cancel_button)
        if hasattr(self, 'add_task_button'):
            self.layout.removeWidget(self.add_task_button)
            self.add_task_button.deleteLater()
        if hasattr(self, 'quick_sort_button'):
            self.layout.removeWidget(self.quick_sort_button)
            self.add_task_button.deleteLater()
        if hasattr(self, 'back_button'):
            self.layout.removeWidget(self.back_button)
            self.back_button.deleteLater()
        if hasattr(self, 'add_list_button'):
            self.layout.removeWidget(self.add_list_button)
            self.add_list_button.deleteLater()

        self.hbox2 = QHBoxLayout()

        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.go_back)
        self.hbox2.addWidget(self.back_button)

        self.quick_sort_button = QPushButton('Chronological Sort', self)
        self.quick_sort_button.clicked.connect(self.quick_sort)
        self.hbox2.addWidget(self.quick_sort_button)

        self.add_list_button = QPushButton('Add a List', self)
        self.add_list_button.clicked.connect(self.open_add_list_window)
        self.hbox2.addWidget(self.add_list_button)

        self.add_task_button = QPushButton('Add Task', self)
        self.add_task_button.clicked.connect(self.open_add_task_window)
        self.hbox2.addWidget(self.add_task_button)

        self.layout.addLayout(self.hbox2)

    def handle_check_click(self):
        sender = self.sender()
        index = self.check_buttons.index(sender)
        task = self.todo_list[index]
        task.task_status = TaskStatus.PASSED
        task_label = self.task_labels[index]
        task_label.setStyleSheet("color: green;")
        task_label.setText("<s>" + task_label.text() + "</s>")
    def handle_x_click(self):
        sender = self.sender()
        index = self.x_buttons.index(sender)
        task = self.todo_list[index]
        task.task_status = TaskStatus.FAILED
        task_label = self.task_labels[index]
        task_label.setStyleSheet("color: red;")
        task_label.setText("<s>" + task_label.text() + "</s>")
    def handle_play_click(self):
        sender = self.sender()
        index = self.play_buttons.index(sender)
        task = self.todo_list[index]
        if sender.text() == "\u25B6":  # play symbol
            sender.setText("\u23F8")  # pause symbol
            task.task_status = TaskStatus.PLAYING
            self.timer_thread = TimerThread(task, self)
            self.timer_thread.timer_signal.connect(lambda x: self.update_duration(task, x))
            self.timer_thread.start()
        else:
            sender.setText("\u25B6")  # play symbol
            task.task_status = TaskStatus.PENDING
            self.timer_thread.paused = not self.timer_thread.paused
    def update_duration(self, task, time_remaining):
        index = self.todo_list.index(task)
        self.todo_list[index].duration = time_remaining
        minute_remaining = self.minutes_remaining[index]
        minute_remaining.setText("Time Left " + str(time_remaining//3600).zfill(2) + ":" + str((time_remaining%3600)//60).zfill(2) + ":" + str(time_remaining%60).zfill(2))
        if (time_remaining == 0):
            task.task_status = TaskStatus.PASSED
            task_label = self.task_labels[index]
            task_label.setStyleSheet("color: green;")
            task_label.setText("<s>" + task_label.text() + "</s>")
            toast = Notification(app_id="Klaus",
                                 title="Reminder",
                                 msg="The timer for " + task.task_name + " is over")
            toast.show()
    def handle_cancel_button(self):
            sender = self.sender()
            index = self.cancel_buttons.index(sender)
            hbox = self.layout.itemAt(index).layout()
            task_label = self.task_labels.pop(index)
            check_button = self.check_buttons.pop(index)
            cancel_button = self.cancel_buttons.pop(index)
            x_button = self.x_buttons.pop(index)
            task = self.todo_list.pop(index)
            self.layout.removeItem(hbox)
            del hbox
            del task_label
            del check_button
            del cancel_button
            del x_button
            del task
            self.parent().show_todolist()
    def open_add_task_window(self):
        self.add_task_window = AddTaskWindow(self, self.todo_list)
        self.add_task_window.show()
    def open_add_list_window(self):
        pass
    def quick_sort(self):
        def task_key(task):
            if task.task_type == TaskType.ACTIVE:
                date_format = "%I:%M %p"
                dt = datetime.strptime(task.due_by, date_format)
                return dt
            elif task.task_type == TaskType.TIMER:
                date_format = "%I:%M %p"
                dt = datetime.strptime(task.due_by, date_format)
                return dt
            elif task.task_type == TaskType.SUSTAIN:
                date_format = "%I:%M %p"
                dt = datetime.strptime(task.endTime, date_format)
                return dt
            elif task.task_type == TaskType.BEDTIME:
                date_format = "%I:%M %p"
                dt = datetime.strptime(task.bed_time, date_format)
                return dt
            else:
                return float('inf')

        self.todo_list = sorted(self.todo_list, key=task_key)
        self.initUI()
    def go_back(self):
        self.parent().initUI()
        pass

class AddTaskWindow(QDialog):
    def __init__(self, parent, todo_list):
        self.todo_list = todo_list
        super().__init__(parent)
        self.reminders = []
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 500, 500)
        self.setWindowTitle("Add Task")

        layout = QVBoxLayout()

        self.error_label = QLabel("Timer Task Require a Duration ")
        self.error_label.setStyleSheet("color: red")
        self.error_label.hide()
        layout.addWidget(self.error_label)



        name_label = QLabel("Name:")
        self.name_edit = QLineEdit()

        layout.addWidget(name_label)
        layout.addWidget(self.name_edit)

        description_label = QLabel("Description:")
        self.description_edit = QTextEdit()

        layout.addWidget(description_label)
        layout.addWidget(self.description_edit)

        type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.addItem("Active")
        self.type_combo.addItem("Timer")
        self.type_combo.addItem("Sustain")
        self.type_combo.addItem("BedTime")
        self.type_combo.currentIndexChanged.connect(self.show_task_type)

        layout.addWidget(type_label)
        layout.addWidget(self.type_combo)

        reminder_label = QLabel("Reminder:")
        self.reminder_edit = QTimeEdit()
        self.add_reminder_button = QPushButton("Add a Reminder")
        self.add_reminder_button.clicked.connect(self.add_to_reminders)

        layout.addWidget(reminder_label)
        layout.addWidget(self.reminder_edit)
        layout.addWidget(self.add_reminder_button)

        due_by_label = QLabel("Due by:")
        self.due_by_edit = QTimeEdit()

        layout.addWidget(due_by_label)
        layout.addWidget(self.due_by_edit)

        self.duration_label = QLabel("Duration:")
        self.duration_edit = QLineEdit()
        self.duration_label.hide()
        self.duration_edit.hide()

        layout.addWidget(self.duration_label)
        layout.addWidget(self.duration_edit)

        self.block_list_label = QLabel("Block List:")
        self.block_list_combo = QComboBox()
        self.block_list_combo.addItem("None")
        self.block_list_combo.addItem("All Apps")
        self.block_list_combo.addItem("Important")
        self.block_list_combo.addItem("Low priority")
        self.block_list_label.hide()
        self.block_list_combo.hide()

        layout.addWidget(self.block_list_label)
        layout.addWidget(self.block_list_combo)

        self.enable_shutdown_checkbox = QCheckBox("Enable Shutdown")
        self.enable_shutdown_checkbox.setCheckState(Qt.Unchecked)
        layout.addWidget(self.enable_shutdown_checkbox)
        self.enable_shutdown_checkbox.hide()

        self.save = QPushButton("Add Task")
        self.save.clicked.connect(self.add_task)
        layout.addWidget(self.save)
        self.setLayout(layout)

    def add_to_reminders(self):
        self.reminders.append(self.reminder_edit.text())

    def add_task(self):
        name = self.name_edit.text()
        description = self.description_edit.toPlainText()
        task_type = self.type_combo.currentText()
        error = False

        if task_type == "Active":
            due_by = self.due_by_edit.text()
            task = ActiveTask(name, description,TaskStatus.PENDING, self.reminders, due_by)

        elif task_type == "Timer":
            due_by = self.due_by_edit.text()
            if (self.duration_edit.text() == ""):
                self.error_label.show()
                error = True
            else:
                duration = int(self.duration_edit.text()) * 60
                block_list = self.block_list_combo.currentText()
                task = TimerTask(name, description, TaskStatus.PENDING, self.reminders, due_by, duration, block_list)
        elif task_type == "Sustain":
            contract = description
            end_time = self.due_by_edit.text()
            task = SustainTask(name, description,TaskStatus.PENDING, contract, end_time)
        elif task_type == "BedTime":
            shutdown = True
            bed_time = self.due_by_edit.text()
            task = BedTime(name, description, TaskStatus.PENDING, bed_time, self.reminders, shutdown)
        if not error:
            self.todo_list.append(task)
            self.reminders = []
            self.parent().initUI()
            self.close()
            self.parent().repaint()
            self.parent().update()
            # Saving the task list to a file
            todoData = {"Tasks": self.todo_list, "Date": datetime.now().date()}
            with open("todo_list.pickle", "wb") as f:
                pickle.dump(todoData, f)
                f.flush()

    def show_task_type(self):
        task_type = self.type_combo.currentText()
        if task_type == "Timer":
            self.duration_label.show()
            self.duration_edit.show()
            self.block_list_label.show()
            self.block_list_combo.show()

        elif task_type == "BedTime":
            self.enable_shutdown_checkbox.show()
        else:
            self.duration_label.hide()
            self.duration_edit.hide()
            self.block_list_label.hide()
            self.block_list_combo.hide()
            self.enable_shutdown_checkbox.hide()

class SettingsWindow(QWidget):
    def __init__(self, todo_list, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        # Create a QLabel widget and set its text
        label = QLabel(self)
        label.setText("This is the Settings window")
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
class ListCreatorWindow(QWidget):
    def __init__(self, todo_list, parent=None):
        super().__init__(parent)
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
                self.list_type_combobox.setCurrentText(data["list_type"])
        except FileNotFoundError:
            self.list_entries_textbox.setPlainText("")
            self.list_type_combobox.setCurrentText("")
    def save_list(self):
        list_name = self.list_name_textbox.text()
        list_type = self.list_type_combobox.currentText()
        list_entries = self.list_entries_textbox.toPlainText()
        entries = list_entries.split(" ")

        data = {
            "list_type": list_type,
            "entries": entries
        }

        with open(f"{list_name}.pickle", "wb") as f:
            pickle.dump(data, f)
class StatsWindow(QWidget):
    def __init__(self, todo_list, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        label = QLabel(self)
        label.setText("This is the Stats window")
class MainWindow(QMainWindow):
    def __init__(self, todo_list, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 1000, 800)
        self.todo_list = todo_list
        self.setWindowTitle("Klaus")
       # self.setStyleSheet("background-color: #36393e;")
        self.initUI()

    def initUI(self):
        todolist_button = QPushButton()
        pixmap = QPixmap("todolist.png")
        todolist_button.setIcon(QIcon(pixmap))
        todolist_button.setIconSize(QSize(150, 150))
        todolist_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        todolist_button.clicked.connect(self.show_todolist)

        settings_button = QPushButton()
        pixmap = QPixmap("setting.png")
        settings_button.setIcon(QIcon(pixmap))
        settings_button.setIconSize(QSize(150, 150))
        settings_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        settings_button.clicked.connect(self.show_settings)

        list_creator_button = QPushButton()
        pixmap = QPixmap("pencil.png")
        list_creator_button.setIcon(QIcon(pixmap))
        list_creator_button.setIconSize(QSize(150, 150))
        list_creator_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        list_creator_button.clicked.connect(self.show_list_creator)

        stats_button = QPushButton()
        pixmap = QPixmap("stats.png")
        stats_button.setIcon(QIcon(pixmap))
        stats_button.setIconSize(QSize(150, 150))
        stats_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        stats_button.clicked.connect(self.show_stats)

        layout = QHBoxLayout()
        layout.addWidget(todolist_button)
        layout.addWidget(settings_button)
        layout.addWidget(list_creator_button)
        layout.addWidget(stats_button)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def show_stats(self):
        stats_window = StatsWindow(self.todo_list)
        self.setCentralWidget(stats_window)

    def show_todolist(self):
        todolist_window = TodoListWindow(self.todo_list)
        self.setCentralWidget(todolist_window)

    def show_settings(self):
        settings_window = SettingsWindow(self.todo_list)
        self.setCentralWidget(settings_window)

    def show_list_creator(self):
        list_creator_window = ListCreatorWindow(self.todo_list)
        self.setCentralWidget(list_creator_window)

    def start_scheduling(self):
        self.schedule_thread = ScheduleThread(self.todo_list, self)
        self.schedule_thread.start()
class ScheduleThread(QThread):
    def __init__(self, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list = todo_list
        self.finished = pyqtSignal()


    def run(self):
        while True:
            current_time = datetime.now().time()
            currentClock = current_time.strftime('%I:%M %p')
            # Check the time and perform the relevant actions
            # For example:
            for task in self.todo_list:
                if task.task_type == TaskType.ACTIVE or task.task_type == TaskType.TIMER or task.task_type == TaskType.BEDTIME:
                    for reminds in task.reminder:
                        reminderTime = reminds
                        timeComponents = reminderTime.split(":")
                        hours = timeComponents[0].zfill(2)
                        minutes = timeComponents[1].split()[0].zfill(2)
                        reminderTime = "{}:{} {}".format(hours, minutes, timeComponents[1].split()[1])
                        if str(currentClock) == str(reminderTime):
                            print("reminder time: " + reminderTime)
                            toast = Notification(app_id="Klaus",
                                                 title="Reminder",
                                                 msg="Reminder to complete the task " + task.task_name)
                            toast.show()

                if task.task_type == TaskType.BEDTIME:
                    originalBedTime = task.bed_time
                    timeComponents = originalBedTime.split(":")
                    hours = timeComponents[0].zfill(2)
                    minutes = timeComponents[1].split()[0].zfill(2)
                    originalBedTime = "{}:{} {}".format(hours, minutes, timeComponents[1].split()[1])

                    if (originalBedTime == currentClock):
                        print("INNIT")
                        toast = Notification(app_id="Klaus",
                                             title="Reminder",
                                             msg="It's bed time, you have 1 minutes before autoshut off", duration="long")
                        toast.show()
                        print("Prepare for shutdown in 60 seconds minutes")
                        subprocess.run("shutdown /s /t 60", shell=True)
                        time.sleep(31)
            # Sleep for some time so that the loop isn't executed too often
            time.sleep(3) # Check every minute



def main():
    todo_list = []
    try:
        with open("todo_list.pickle", "rb") as f:
            todoData = pickle.load(f)
            todo_list = todoData["Tasks"]
            timeStamp = todoData["Date"]
    except:
        # Handle the exception and continue without the data
        todo_list = []
        pass

    #If it's past 7am, and the datetime of the last todolist edit was not today, you're forced to make a todolist.
    if (datetime.now().hour >= 7 and datetime.now().date() != timeStamp):
        print("DEBUGGING 131")

    neo_todo_list  = []
    act_task = ActiveTask("Drink Water", "...", TaskStatus.PENDING, "15 til", '11:59 PM')
    time_task = TimerTask("30 Minute Meditation", "...", TaskStatus.PENDING, "15 til", '11:59 PM', 120, "None")
    sus_task = SustainTask("No Weed", "...", TaskStatus.PENDING, "contract", '11:59 PM')
    sus_task2 = SustainTask("Porn Abstinence", "...", TaskStatus.PENDING, "contract", '11:59 PM')
    sus_task3 = SustainTask("OMAD", "...", TaskStatus.PENDING, "contract", '8:00 PM')
    act_task2 = ActiveTask("Walk", "...", TaskStatus.PENDING, "15 til", '11:59 PM')
    bed_task = BedTime("Sleep at midnight", "...", TaskStatus.PENDING, '11:59 PM', "15 til", True)
    act_task3 = ActiveTask("Cold Shower", "...", TaskStatus.PENDING, "15 til", '11:59 PM')
    neo_todo_list.append(sus_task)
    neo_todo_list.append(bed_task)
    neo_todo_list.append(time_task)
    neo_todo_list.append(sus_task2)
    neo_todo_list.append(act_task2)
    neo_todo_list.append(sus_task3)
    neo_todo_list.append(act_task3)
    neo_todo_list.append(act_task)

    x = False
    if (x == True):
        todo_list.extend(neo_todo_list)


    app = QApplication([])
    font = QFont("Arial", 15)
    app.setFont(font)
    main_window = MainWindow(todo_list)
    main_window.show()
    main_window.start_scheduling()
    app.exec()


if __name__ == '__main__':
    main()