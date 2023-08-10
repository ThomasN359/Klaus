from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QTableWidget, QHeaderView, QWidget, QDateEdit
)
import calendar

from KlausSrc.Utilities.config import iconDirectory
from KlausSrc.Utilities.HelperFunctions import makePath, create_button_with_pixmap
from KlausSrc.PopUpWindows.MemoPopUp import MemoPopUp
from KlausSrc.PopUpWindows.SchedulerPopUp import SchedulerPopUp
import datetime


class CalendarWindow(QMainWindow):
    def __init__(self, settings, todo_list, parent=None):
        super().__init__(parent)
        self.clicked_date = None
        self.settings = settings
        self.todo_list = todo_list
        self.setWindowTitle("Calendar Pop-Up")
        self.setGeometry(0, 0, 1100, 800)  # Set geometry of the QMainWindow

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

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
        self.calendar_table.setHorizontalHeaderLabels(
            ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.calendar_table.verticalHeader().setVisible(False)  # Remove the row labels
        self.calendar_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.calendar_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Resize 'Wednesday' column
        self.calendar_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.populate_calendar(self.current_year, self.current_month)
        layout.addWidget(self.calendar_table)

        self.calendar_table.cellClicked.connect(self.cell_clicked)

    def populate_calendar(self, year, month):
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
                    pixmap = makePath(iconDirectory, "scheduler.png")
                    self.streak_button = create_button_with_pixmap(pixmap, (20, 20), self.streak_button_clicked)
                    self.streak_button.setStyleSheet("background-color: #e24545")  # set gray background color
                    self.streak_button.setFixedSize(25, 25)  # set fixed size of 30x30 pixels
                    button_layout.addWidget(self.streak_button)

                    # Create and add the todo list button to the button layout
                    pixmap = makePath(iconDirectory, "todolist.png")
                    self.todo_list_button = create_button_with_pixmap(pixmap, (20, 20), self.todo_list_button_clicked)
                    self.todo_list_button.setStyleSheet("background-color: white")
                    self.todo_list_button.setFixedSize(25 , 25)
                    button_layout.addWidget(self.todo_list_button)

                    # create memo button
                    pixmap = makePath(iconDirectory, "memo.png")
                    self.memo_button = create_button_with_pixmap(pixmap, (20, 20), self.memo_button_clicked)
                    self.memo_button.setStyleSheet("background-color: orange")
                    self.memo_button.setFixedSize(25, 25)
                    button_layout.addWidget(self.memo_button)

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
        popup = SchedulerPopUp(self, self.todo_list)
        popup.exec()

    def todo_list_button_clicked(self):
        if not self.clicked_date:
            source_widget = self.sender().parentWidget()
            for i in range(self.calendar_table.rowCount()):
                for j in range(self.calendar_table.columnCount()):
                    if self.calendar_table.cellWidget(i, j) == source_widget:
                        day = source_widget.findChild(QLabel).text()
                        self.clicked_date = datetime.date(self.current_year, self.current_month, int(day))
                        break

        if self.clicked_date:
            self.parent().timeStamp = self.clicked_date
            self.parent().show_todolist()


    def memo_button_clicked(self):
        popup = MemoPopUp(self)
        popup.exec()

    def cell_clicked(self, row, column):
        # This will get the date from the clicked cell in the QTableWidget
        day = self.calendar_table.cellWidget(row, column).findChild(QLabel).text()
        self.clicked_date = datetime.date(self.current_year, self.current_month, int(day))
