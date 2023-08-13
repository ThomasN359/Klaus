import os
import pickle
import time
from datetime import datetime
from functools import partial

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QTimeEdit, QComboBox, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QWidget, \
    QTabWidget, QDialog, QScrollArea

from KlausSrc.PopUpWindows.AddTaskWindow import AddTaskWindow
from KlausSrc.Utilities.config import iconDirectory, pickleDirectory
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath
from KlausSrc.Objects.Task import TaskType, AddMethod


class SchedulerPopUp(QDialog):
    def __init__(self, parent, settings, todo_list, todo_list_archive, block_list, scheduler):
        super().__init__(parent)
        self.block_list = block_list
        self.todo_list_archive = todo_list_archive
        self.scheduler = scheduler
        self.todo_list = todo_list
        self.settings = settings
        self.setWindowTitle("Streak Pop-Up")

        self.tab_widget = QTabWidget()

        # Create tabs
        self.scheduler_tab = QWidget()
        self.streak_tab = QWidget()
        self.weekday_tab = QWidget()  # Add a Bedtime Scheduler tab

        # Add tabs to QTabWidget
        self.tab_widget.addTab(self.scheduler_tab, "Timer Scheduler")
        self.tab_widget.addTab(self.streak_tab, "Streak Scheduler")
        self.tab_widget.addTab(self.weekday_tab, "Bedtime Scheduler")  # Add Bedtime Scheduler tab to tab_widget

        # Scheduler Tab
        self.scheduler_layout = QVBoxLayout(self.scheduler_tab)

        self.scheduler_label = QLabel("Select a forced start time for timer tasks")
        self.scheduler_layout.addWidget(self.scheduler_label)

        self.add_task_button = QPushButton("+")
        self.add_task_button.clicked.connect(self.add_task_row)
        self.scheduler_layout.addWidget(self.add_task_button)

        self.task_rows = []
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_data)
        self.scheduler_layout.addWidget(self.save_button)

        # Streak Tab
        self.streak_layout = QVBoxLayout(self.streak_tab)
        self.streak_label = QLabel(
            "Keep track of sustained tasks and allow adding them to be automated while counting\n"
            " streaks. You can also customize streak rules such allowing 1 X per week.")
        self.streak_layout.addWidget(self.streak_label)

        # Weekday Scheduler Tab
        self.weekday_layout = QVBoxLayout(self.weekday_tab)

        self.scroll_area = QScrollArea(self.weekday_tab)
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.weekday_layout.addWidget(self.scroll_area)

        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.days_of_week = ['SUNDAY', 'MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY']

        self.day_layouts = {}  # A dictionary to hold QVBoxLayouts for each day

        for day in self.days_of_week:
            day_layout = QVBoxLayout()
            self.day_layouts[day] = day_layout  # Store the layout for later access

            day_label = QLabel(day)
            day_layout.addWidget(day_label)

            # We'll move the '+' button creation to the redraw_tasks method so it's always at the bottom
            self.scroll_layout.addLayout(day_layout)

        # Create the Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.on_apply_click)
        self.weekday_layout.addWidget(self.apply_button)

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)
        self.redraw_tasks()

    def on_apply_click(self):
        # Get the current date
        current_date = datetime.now().date()

        # Loop over keys (dates) in the todo_list_archive dictionary
        for date_obj, tasks in list(
                self.todo_list_archive.items()):  # using list() to ensure we can modify the dict safely

            # Only modify dates that are in the future
            if date_obj > current_date:
                # Filter tasks to keep only those added manually
                manually_added_tasks = [task for task in tasks if task.add_method == AddMethod.MANUAL]

                # Clear the tasks for that date (effectively removing all)
                self.todo_list_archive[date_obj] = []

                # Now, add back the manually added tasks
                self.todo_list_archive[date_obj].extend(manually_added_tasks)

                # Get the day name like "MONDAY", "TUESDAY", etc.
                day_name = date_obj.strftime('%A').upper()

                # Check if the day exists in the scheduler
                if day_name in self.scheduler:
                    # Append tasks from the scheduler to the archive for that date
                    self.todo_list_archive[date_obj].extend(self.scheduler[day_name])

        # Save using parent's save() method, if available
        if hasattr(self.parent(), 'save'):
            self.parent().save()

    def add_row(self, day_name):
        add_method_value = getattr(AddMethod, day_name.upper())
        self.add_task_window = AddTaskWindow(self, self.todo_list_archive, self.todo_list, self.block_list,
                                             self.settings, self.scheduler, -1, add_method_value)

        # Connect window's close signal to redraw
        self.add_task_window.window_closed.connect(self.redraw_tasks)
        self.add_task_window.show()
        self.redraw_tasks()

    def on_drop_click(self, task, day):
        # Remove the task from the scheduler for the given day
        for tasks in self.scheduler[day]:
            if tasks.task_name == task.task_name:
                self.scheduler[day].remove(tasks)

        self.save_data()
        # Save the updated scheduler
        self.save_scheduler()

        # Redraw the tasks
        self.redraw_tasks()

    def redraw_tasks(self):
        with open(makePath(pickleDirectory, 'scheduler.pickle'), 'rb') as file:
            scheduler_data = pickle.load(file)
            scheduler = scheduler_data["scheduler"]

        for day, tasks in scheduler.items():
            layout = self.day_layouts[day]

            # Clearing existing tasks
            for i in reversed(range(layout.count())):  # loop backward to safely remove widgets
                widget = layout.itemAt(i).widget()
                if widget is not None and widget.objectName() != "dayLabel":  # we won't delete day labels
                    widget.deleteLater()  # properly delete the widget

            # Adding tasks from scheduler
            for task in tasks:
                task_hbox = QHBoxLayout()
                task_label = QLabel(task.task_name)
                drop_button = QPushButton('Drop')
                drop_button.clicked.connect(partial(self.on_drop_click, task, day))

                task_hbox.addWidget(task_label)
                task_hbox.addWidget(drop_button)

                wrapper_widget = QWidget()  # We use a wrapper widget to encapsulate the QHBoxLayout
                wrapper_widget.setLayout(task_hbox)
                layout.addWidget(wrapper_widget)  # Add the hbox to the day's QVBoxLayout

            # After adding all tasks for a day, add the '+' button at the bottom
            add_button = QPushButton('+')
            add_button.clicked.connect(partial(self.add_row, day))
            layout.addWidget(add_button)

    def add_task_row(self):
        task_row_layout = QHBoxLayout()
        task_combobox = QComboBox()
        task_combobox.addItem("None")
        for task in self.todo_list:
            if task.task_type == TaskType.TIMER:
                task_combobox.addItem(task.task_name)
        task_row_layout.addWidget(task_combobox)

        self.task_start_time = QTimeEdit()
        task_row_layout.addWidget(self.task_start_time)

        pixmap = makePath(iconDirectory, "unlock.png")
        lock_button = create_button_with_pixmap(pixmap, (20,20), self.handle_lockIn)
        lock_button.setStyleSheet("color: gray")
        task_row_layout.addWidget(lock_button)

        delete_button = QPushButton("\u26A0")
        delete_button.setFont(QFont("Arial", 10))
        delete_button.setStyleSheet("color: yellow")
        task_row_layout.addWidget(delete_button)

        self.task_rows.append((task_combobox, self.task_start_time, lock_button, delete_button))
        self.scheduler_layout.insertLayout(self.scheduler_layout.count()-1, task_row_layout)


    def save_scheduler(self):
        with open(makePath(pickleDirectory, 'scheduler.pickle'), 'wb') as f:
            data = {"scheduler": self.scheduler, "type": "scheduler"}
            pickle.dump(data, f)
            f.flush()

    def handle_lockIn(self):
        pass

    def save_data(self):
        for task_row in self.task_rows:
            task_combobox, task_time_edit, _, _ = task_row
            task_name = task_combobox.currentText()

            # Find the corresponding task in the todo_list
            for task in self.todo_list:
                if task.task_name == task_name:
                    task.start_by = task_time_edit.time().toString("hh:mm AP")
                    print("Set task for" + task.task_name)
                    break

        todoData = {"tasks": self.todo_list, "date": datetime.now().date(), "type": "TODOLIST"}
        pickle_file_path = os.path.join(pickleDirectory, "todo_list.pickle")
        with open(pickle_file_path, "wb") as f:
            pickle.dump(todoData, f)
