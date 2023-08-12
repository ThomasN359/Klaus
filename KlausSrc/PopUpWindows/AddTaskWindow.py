import os
import pickle
from datetime import datetime
from KlausSrc.Utilities.config import pickleDirectory
from PyQt5.QtCore import QTime, Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QTextEdit, QLineEdit, QVBoxLayout, QDialog, QTimeEdit, \
    QCheckBox
from KlausSrc.Objects.Task import TaskStatus, TaskType, ActiveTask, TimerTask, BedTime, SustainTask, AddMethod
from KlausSrc.Utilities.HelperFunctions import makePath


class AddTaskWindow(QDialog):
    # index denotes the hbox index for the task line widget
    def __init__(self, parent, todo_list_archive, todo_list, block_list, settings, scheduler, index, add_method):
        self.add_Method = add_method
        self.scheduler = scheduler
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
        self.setStyleSheet("background-color: none;")

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

        # IF there exist a bedtime, then use it to set the due by time
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
            with open(makePath(pickleDirectory, filename), "rb") as f:
                data = pickle.load(f)
                if data["type"] == "APPLIST":
                    self.app_block_list_combo.addItem(filename)

        self.app_block_list_label.hide()
        self.app_block_list_combo.hide()

        self.web_block_list_label = QLabel("Web Block List:")
        self.web_block_list_combo = QComboBox()
        self.web_block_list_combo.addItem("None")

        for filename in os.listdir(pickleDirectory):
            with open(makePath(pickleDirectory, filename), "rb") as f:
                data = pickle.load(f)
                if data["type"] == "WEBLIST":
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
            task = ActiveTask(name, description, TaskStatus.PENDING, self.add_Method, self.reminders, due_by)
        elif task_type == "Timer":
            due_by = self.due_by_edit.text()
            if self.duration_edit.text() == "":
                self.error_label.show()
                error = True
            else:
                duration = int(self.duration_edit.text()) * 60
                app_block_list = self.app_block_list_combo.currentText()
                web_block_list = self.web_block_list_combo.currentText()
                task = TimerTask(name, description, TaskStatus.PENDING, self.add_Method, self.reminders, due_by, None, duration,
                                 app_block_list, web_block_list)
        elif task_type == "Sustain":
            contract = description
            end_time = self.due_by_edit.text()
            task = SustainTask(name, description, TaskStatus.PENDING, self.add_Method, contract, end_time)
        elif task_type == "BedTime":
            shutdown = True
            due_by = self.due_by_edit.text()
            task = BedTime(name, description, TaskStatus.PENDING, self.add_Method, due_by, self.reminders, shutdown)
        if not error:
            self.has_daily_block = False
            self.block_list[0][0] = []

            if self.index == self.ADD_TASK:
                self.todo_list.append(task)
            elif self.add_Method == AddMethod.MANUAL:
                self.todo_list[self.index] = task
            else:
                print("add on monday ya")
            self.reminders = []

            # Define the mapping outside the function for clarity
            ADD_METHOD_TO_DAY = {
                AddMethod.MONDAY: "MONDAY",
                AddMethod.TUESDAY: "TUESDAY",
                AddMethod.WEDNESDAY: "WEDNESDAY",
                AddMethod.THURSDAY: "THURSDAY",
                AddMethod.FRIDAY: "FRIDAY",
                AddMethod.SATURDAY: "SATURDAY",
                AddMethod.SUNDAY: "SUNDAY",
            }

            # Now, inside your function
            if self.add_Method == AddMethod.MANUAL:
                self.parent().initUI()
                self.close()
                self.parent().repaint()
                self.parent().update()
                # Saving the task list to a file
                update_file(self)
            else:
                day_name = ADD_METHOD_TO_DAY.get(self.add_Method)
                if day_name:
                    task.add_method = self.add_Method
                    self.scheduler[day_name].append(task)
                    self.save_scheduler()
                    self.close()




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


    def save_scheduler(self):
        with open(makePath(pickleDirectory, 'scheduler.pickle'), 'wb') as f:
            data = {"scheduler": self.scheduler, "type": "scheduler"}
            pickle.dump(data, f)
            f.flush()


def update_file(self):
    self.parent().save()
    # todoData = {"tasks": self.todo_list, "date": datetime.now().date(), "type": "TODOLIST"}
    # with open(makePath(pickleDirectory, "todo_list.pickle"), "wb") as f:
    #     pickle.dump(todoData, f)
    #     f.flush()
