from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.uic.Compiler.qtproxies import QtCore
import random
import calendar
import datetime
from HelperFunctions import save_setting, create_button_with_pixmap
from Task import TaskType
from config import pictureDirectory
from Settings import *


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


class LockInPopUp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings
        if self.settings.lock_in == False:
            self.setWindowTitle("Lock In Pop-Up")

            layout = QVBoxLayout()

            message_label = QLabel("By locking the todo-list you can no longer remove unwanted tasks?")
            layout.addWidget(message_label)

            yes_button = QPushButton("Yes")
            yes_button.clicked.connect(self.yes_button_clicked)
            layout.addWidget(yes_button)

            no_button = QPushButton("No")
            no_button.clicked.connect(self.no_button_clicked)
            layout.addWidget(no_button)

            self.setLayout(layout)
        else:
            layout = QVBoxLayout()
            message_label = QLabel("It is currently locked")
            ok_button = QPushButton("Ok")
            ok_button.clicked.connect(self.no_button_clicked)
            layout.addWidget(message_label)
            layout.addWidget(ok_button)
            self.setLayout(layout)

    def yes_button_clicked(self):
        self.settings.lock_in = True
        self.parent().refresh_save()
        save_setting(self.settings)
        print("Lock in set to true")
        self.close()


    def no_button_clicked(self):
        self.close()
        print("Closed popup window")


class StreakPopUp(QDialog):
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

        pixmap = makePath(pictureDirectory, "unlock.png")
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
class MemoPopUp(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings
        self.setWindowTitle("Memo Pop-Up")

        # Create main layout
        layout = QVBoxLayout()

        # Create QLabel and add it to the layout
        message_label = QLabel("Write and save a memo for this day. These logs will be sent\n to other user stats and can"
                               " be viewed in other windows later.\n Note no code is done besides \nthe UI so saving doesn't "
                               "do anything")
        layout.addWidget(message_label)

        # Create large text field (QTextEdit) and add it to the layout
        self.text_field = QTextEdit()
        layout.addWidget(self.text_field)

        # Create Save and Close buttons, and their layout
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_clicked)
        close_button = QPushButton('Close')
        close_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(close_button)

        # Add buttons layout to the main layout
        layout.addLayout(buttons_layout)

        # Set main layout
        self.setLayout(layout)

    def save_clicked(self):
        # Update button text and style sheet
        self.save_button.setText('Saved')
        self.save_button.setStyleSheet('background-color: green')

        # Create a QTimer to revert the changes after one second
        QTimer.singleShot(1000, self.reset_save_button)

    def reset_save_button(self):
        # Revert button text and style sheet
        self.save_button.setText('Save')
        self.save_button.setStyleSheet('')


class CalendarPopUp(QDialog):
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Calendar Pop-Up")
        self.setGeometry(0, 0, 1100, 800)  # Set geometry of the QDialog

        layout = QVBoxLayout()

        self.current_month = datetime.date.today().month
        self.current_year = datetime.date.today().year
        self.current_day = datetime.date.today().day

        # Create the month label and add it to the layout
        self.month_label = QLabel(calendar.month_name[self.current_month])

        # Create previous and next buttons for month navigation
        self.prev_button = QPushButton("←", self)
        self.prev_button.clicked.connect(self.prev_month)

        # Create date picker
        self.date_picker = QDateEdit(calendarPopup=True)
        self.date_picker.setDateTime(datetime.datetime.now())
        self.date_picker.dateChanged.connect(self.date_changed)

        self.next_button = QPushButton("→", self)
        self.next_button.clicked.connect(self.next_month)

        # Add the month label and navigation buttons to a horizontal layout
        month_layout = QHBoxLayout()
        month_layout.addWidget(self.prev_button)
        month_layout.addWidget(self.month_label, alignment=Qt.AlignCenter)
        month_layout.addWidget(self.date_picker)
        month_layout.addWidget(self.next_button)

        layout.addLayout(month_layout)

        # Create the table for the calendar
        self.calendar_table = QTableWidget(5, 7)  # 5 weeks, 7 days a week
        self.calendar_table.setHorizontalHeaderLabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.calendar_table.verticalHeader().setVisible(False)  # Remove the row labels
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.calendar_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Resize 'Wednesday' column
        self.calendar_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.populate_calendar(self.current_year, self.current_month)
        layout.addWidget(self.calendar_table)

        self.setLayout(layout)

    def populate_calendar(self, year, month):
        # First, clear the table
        self.calendar_table.clearContents()

        # Get the first day of the month and the number of days in the month
        month_calendar = calendar.monthcalendar(year, month)

        # First, clear the table
        self.calendar_table.clearContents()

        # Get the first day of the month and the number of days in the month
        month_calendar = calendar.monthcalendar(year, month)

        for i, week in enumerate(month_calendar):
            for j, day in enumerate(week):
                if day != 0:  # calendar.monthcalendar() pads with 0s to fill weeks
                    # Create a widget for the cell
                    widget = QWidget()

                    # Create a vertical layout for the cell
                    cell_layout = QVBoxLayout()
                    cell_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Set the alignment to top left
                    cell_layout.setSpacing(0)  # Remove spacing between the elements
                    cell_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
                    widget.setLayout(cell_layout)

                    # Add the day label to the cell
                    item = QLabel(str(day))
                    item.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Position the text to top left
                    cell_layout.addWidget(item)

                    # Create a horizontal layout for the buttons
                    button_layout = QHBoxLayout()
                    button_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Set the alignment to top left
                    button_layout.setSpacing(0)  # Remove spacing between the buttons
                    button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins

                    # Create and add the streak button to the button layout
                    pixmap = makePath(pictureDirectory, "streak.png")
                    self.streak_button = create_button_with_pixmap(pixmap, (20, 20), self.streak_button_clicked)
                    self.streak_button.setStyleSheet("background-color: #ffff00")  # set gray background color
                    self.streak_button.setFixedSize(25, 25)  # set fixed size of 30x30 pixels
                    button_layout.addWidget(self.streak_button)

                    # Create and add the todo list button to the button layout
                    pixmap = makePath(pictureDirectory, "todolist.png")
                    self.todo_list_button = create_button_with_pixmap(pixmap, (20, 20), self.todo_list_button_clicked)
                    self.todo_list_button.setStyleSheet("background-color: white")
                    self.todo_list_button.setFixedSize(25 , 25)
                    button_layout.addWidget(self.todo_list_button)

                    # Add the button layout to the cell layout
                    cell_layout.addLayout(button_layout)

                    # Add the widget to the table
                    self.calendar_table.setCellWidget(i, j, widget)

                    # Highlight the current day
                    today = datetime.date.today()
                    if day == today.day and month == today.month and year == today.year:
                        self.calendar_table.cellWidget(i, j).setStyleSheet(
                            'background-color: rgb(100, 149, 237);')  # Cornflower Blue color
    def prev_month(self):
        # Decrease the month, and decrease the year if necessary
        self.current_month -= 1
        if self.current_month == 0:
            self.current_month = 12
            self.current_year -= 1

        self.month_label.setText(calendar.month_name[self.current_month])
        self.populate_calendar(self.current_year, self.current_month)

    def next_month(self):
        # Increase the month, and increase the year if necessary
        self.current_month += 1
        if self.current_month == 13:
            self.current_month = 1
            self.current_year += 1

        self.month_label.setText(calendar.month_name[self.current_month])
        self.populate_calendar(self.current_year, self.current_month)

    def date_changed(self, date):
        self.current_year = date.year()
        self.current_month = date.month()
        self.month_label.setText(calendar.month_name[self.current_month])
        self.populate_calendar(self.current_year, self.current_month)

    def streak_button_clicked(self):
        popup = StreakPopUp(self)
        popup.exec()

    def todo_list_button_clicked(self):
        print(datetime.datetime.now().strftime('%Y-%m-%d'))