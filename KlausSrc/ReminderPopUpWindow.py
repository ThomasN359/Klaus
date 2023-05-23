from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *
from PyQt5.uic.Compiler.qtproxies import QtCore
import random
import calendar
import datetime
from HelperFunctions import save_setting
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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = parent.settings
        self.setWindowTitle("Streak Pop-Up")

        self.tab_widget = QTabWidget()

        self.scheduler_tab = QWidget()
        self.streak_tab = QWidget()

        self.tab_widget.addTab(self.scheduler_tab, "Scheduler")
        self.tab_widget.addTab(self.streak_tab, "Streak")

        self.scheduler_layout = QVBoxLayout(self.scheduler_tab)
        self.scheduler_label = QLabel("Schedule timer tasks to start automatically by setting a proper time. You can\n "
                                      "choose if you want to lock in the task if you haven't already")
        self.scheduler_layout.addWidget(self.scheduler_label)

        self.streak_layout = QVBoxLayout(self.streak_tab)
        self.streak_label = QLabel("Keep track of sustained tasks and allow adding them to be automated while counting\n"
                                   " streaks. You can also customize streak rules such allowing 1 X per week.")
        self.streak_layout.addWidget(self.streak_label)

        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)


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
    def __init__(self, parent=None):
        super().__init__(parent)
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

        for i, week in enumerate(month_calendar):
            for j, day in enumerate(week):
                if day != 0:  # calendar.monthcalendar() pads with 0s to fill weeks
                    item = QTableWidgetItem(str(day))
                    item.setTextAlignment(Qt.AlignTop | Qt.AlignLeft)  # Position the text to top left
                    self.calendar_table.setItem(i, j, item)

                    # Highlight the current day
                    today = datetime.date.today()
                    if day == today.day and month == today.month and year == today.year:
                        self.calendar_table.item(i, j).setBackground(QColor(100, 149, 237))  # Cornflower Blue color

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
