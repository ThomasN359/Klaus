from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QTimeEdit, QComboBox, QHBoxLayout, QVBoxLayout, QCheckBox, QLabel, QWidget, \
    QTabWidget, QDialog

from KlausSrc.Utilities.config import iconDirectory
from KlausSrc.Utilities.HelperFunctions import create_button_with_pixmap, makePath
from KlausSrc.Objects.Task import TaskType

class SchedulerPopUp(QDialog):
    def __init__(self, settings, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list = todo_list
        self.settings = settings
        self.setWindowTitle("Streak Pop-Up")

        self.tab_widget = QTabWidget()

        # Create tabs
        self.scheduler_tab = QWidget()
        self.streak_tab = QWidget()
        self.bedtime_tab = QWidget()  # Add a Bedtime Scheduler tab

        # Add tabs to QTabWidget
        self.tab_widget.addTab(self.scheduler_tab, "Timer Scheduler")
        self.tab_widget.addTab(self.streak_tab, "Streak Scheduler")
        self.tab_widget.addTab(self.bedtime_tab, "Bedtime Scheduler")  # Add Bedtime Scheduler tab to tab_widget

        # Scheduler Tab
        self.scheduler_layout = QVBoxLayout(self.scheduler_tab)

        self.scheduler_label = QLabel("Select a forced start time for timer tasks")
        self.scheduler_layout.addWidget(self.scheduler_label)

        self.add_task_button = QPushButton("+")
        self.add_task_button.clicked.connect(self.add_task_row)
        self.scheduler_layout.addWidget(self.add_task_button)

        self.task_rows = []

        # Streak Tab
        self.streak_layout = QVBoxLayout(self.streak_tab)
        self.streak_label = QLabel(
            "Keep track of sustained tasks and allow adding them to be automated while counting\n"
            " streaks. You can also customize streak rules such allowing 1 X per week.")
        self.streak_layout.addWidget(self.streak_label)

        # Bedtime Scheduler Tab
        self.bedtime_layout = QVBoxLayout(self.bedtime_tab)

        self.days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        for day in self.days_of_week:
            day_layout = QHBoxLayout()

            # Create and add the day label
            day_label = QLabel(day)
            day_layout.addWidget(day_label)

            # Create and add the QTimeEdit widget for bedtime selection
            bedtime_time_edit = QTimeEdit()
            bedtime_time_edit.setDisplayFormat("HH:mm")  # 24-hour format
            day_layout.addWidget(bedtime_time_edit)

            # Create and add a checkbox for enabling/disabling the bedtime
            bedtime_checkbox = QCheckBox("Enable bedtime")
            day_layout.addWidget(bedtime_checkbox)

            # Create gear button
            gear_button = QPushButton("\u2699")
            gear_button.setFont(QFont("Arial", 10))
            gear_button.setStyleSheet("color: gray")
            day_layout.addWidget(gear_button)  # add gear button to the day layout

            self.bedtime_layout.addLayout(day_layout)

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)

    def add_task_row(self):
        task_row_layout = QHBoxLayout()

        task_combobox = QComboBox()
        # Add some dummy task names, replace this with your actual task names
        for task in self.todo_list:
            if task.task_type == TaskType.TIMER:
                task_combobox.addItem(task.task_name)
        task_combobox.addItem("None")
        task_row_layout.addWidget(task_combobox)

        task_time_edit = QTimeEdit()
        task_time_edit.setDisplayFormat("HH:mm")  # 24-hour format
        task_row_layout.addWidget(task_time_edit)

        pixmap = makePath(iconDirectory, "unlock.png")
        lock_button = create_button_with_pixmap(pixmap, (20,20), self.handle_lockIn)
        lock_button.setStyleSheet("color: gray")
        task_row_layout.addWidget(lock_button)

        delete_button = QPushButton("\u26A0")
        delete_button.setFont(QFont("Arial", 10))
        delete_button.setStyleSheet("color: yellow")
        task_row_layout.addWidget(delete_button)

        self.task_rows.append((task_combobox, task_time_edit, lock_button, delete_button))
        self.scheduler_layout.insertLayout(self.scheduler_layout.count()-1, task_row_layout)

    def handle_lockIn(self):
        pass
