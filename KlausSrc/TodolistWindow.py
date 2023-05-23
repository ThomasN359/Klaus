import pickle
from Task import TaskType, TaskStatus
from Settings import KlausFeeling
from GlobalThreads import TimerThread
from config import pickleDirectory, pictureDirectory
import random
import os
from datetime import *
from PyQt5 import QtCore
from winotify import Notification
from PyQt5.QtCore import QTime, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *
from ReminderPopUpWindow import ReminderPopUp, LockInPopUp, MemoPopUp, StreakPopUp, CalendarPopUp
from HelperFunctions import automate_browser
from AddTaskWindow import AddTaskWindow
from AddTaskWindow import update_file
from QuickListAddWindow import QuickListAddWindow
from HelperFunctions import makePath


class TodoListWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, block_list, settings, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_list = block_list
        self.settings = settings
        self.task_labels = []
        self.check_buttons = []
        self.x_buttons = []
        self.play_buttons = []
        self.timer_lock_in_buttons = []
        self.cancel_buttons = []
        self.minutes_remaining = []
        self.gear_buttons = []
        self.layout = QVBoxLayout()
        self.initUI()
        self.setLayout(self.layout)

    def initUI(self):

        # Clear the horizontal box for the title row to avoid duplicates each refresh
        if hasattr(self, 'title_layout'):
            index = self.layout.indexOf(self.title_layout)
            layout = self.layout.takeAt(index)
            self.clear_layout(layout)

        # Here is where the top horizontal row is made, this includes the Todolist, The date, and arrows to navigate
        self.label = QLabel(self)
        self.label.setText(f"{datetime.now().strftime('%Y-%m-%d')} Todo List")
        font = self.label.font()
        font.setPointSize(20)
        self.label.setFont(font)
        self.left_button = QPushButton("←", self)
        self.right_button = QPushButton("→", self)
        self.left_button.setFixedSize(40, 30)
        self.title_layout = QHBoxLayout()
        self.right_button.setFixedSize(40, 30)
        self.title_layout.addStretch(1)
        self.title_layout.addWidget(self.left_button)
        self.title_layout.addWidget(self.label)
        self.title_layout.addWidget(self.right_button)
        self.title_layout.addStretch(1)
        self.title_layout.addStretch()

        # Set spacing between widgets in title_layout to 0
        self.layout.addLayout(self.title_layout)

        # This code block delete the sub_title_layout to prevent it from being redrawn
        if hasattr(self, 'sub_title_layout'):
            index = self.layout.indexOf(self.sub_title_layout)
            layout = self.layout.takeAt(index)
            self.clear_layout(layout)
            self.sub_title_layout = QHBoxLayout()

        # This next section is where the buttons below the title layout is created
        self.sub_title_layout = QHBoxLayout()


        # Lock button
        self.lock_button = QPushButton()
        pixmap = QPixmap(makePath(pictureDirectory, "lock.png"))
        self.lock_button.setIcon(QIcon(pixmap))
        self.lock_button.setIconSize(QSize(30, 30))
        self.lock_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.lock_button.clicked.connect(self.lockIn)
        self.lock_button.setStyleSheet("background-color: #cfcfcf")  # set gray background color
        self.lock_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Streak Button
        self.streak_button = QPushButton()
        pixmap = QPixmap(makePath(pictureDirectory, "streak.png"))
        self.streak_button.setIcon(QIcon(pixmap))
        self.streak_button.setIconSize(QSize(30, 30))
        self.streak_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.streak_button.clicked.connect(self.handle_streak_button)
        self.streak_button.setStyleSheet("background-color: #ffff00")  # set gray background color
        self.streak_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Memo Button
        self.memo_button = QPushButton()
        pixmap = QPixmap(makePath(pictureDirectory, "memo.png"))
        self.memo_button.setIcon(QIcon(pixmap))
        self.memo_button.setIconSize(QSize(30, 30))
        self.memo_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.memo_button.clicked.connect(self.handle_memo_button)
        self.memo_button.setStyleSheet("background-color: #ffb200")  # set gray background color
        self.memo_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Refresh Button
        self.refresh_button = QPushButton()
        pixmap = QPixmap(makePath(pictureDirectory, "refresh_icon.png"))
        self.refresh_button.setIcon(QIcon(pixmap))
        self.refresh_button.setIconSize(QSize(30, 30))
        self.refresh_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.refresh_button.clicked.connect(self.refresh_save)
        self.refresh_button.setStyleSheet("background-color: #00ff00")  # set gray background color
        self.refresh_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Calendar Button
        self.calendar_button = QPushButton()
        pixmap = QPixmap(makePath(pictureDirectory, "calender.png"))
        self.calendar_button.setIcon(QIcon(pixmap))
        self.calendar_button.setIconSize(QSize(30, 30))
        self.calendar_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.calendar_button.clicked.connect(self.handle_calendar_button)
        self.calendar_button.setStyleSheet("background-color: #00ffff")  # set gray background color
        self.calendar_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        self.sub_title_layout.addStretch(1)
        self.sub_title_layout.addWidget(self.refresh_button)
        self.sub_title_layout.addWidget(self.memo_button)
        self.sub_title_layout.addWidget(self.lock_button)
        self.sub_title_layout.addWidget(self.streak_button)
        self.sub_title_layout.addWidget(self.calendar_button)
        self.sub_title_layout.addStretch(1)
        self.layout.addLayout(self.sub_title_layout)

        # Below is the code that draws the timer row
        if hasattr(self, 'hlayout'):
            index = self.layout.indexOf(self.hlayout)
            layout = self.layout.takeAt(index)
            self.clear_layout(layout)
            self.sub_hlayout = QHBoxLayout()

        self.hlayout = QHBoxLayout()

        # Current Time Label
        self.current_time_label = QLabel("Current Time:")
        self.current_time_display = QLabel()
        self.updateCurrentTime()

        # Timer Accounted Label
        self.timer_accounted_time_label = QLabel("Timer Accounted:")
        self.timer_accounted_time_display = QLabel()
        self.updateTimerAccountedTime()

        # Bedtime Label
        self.bedtime_label = QLabel("Bedtime:")
        self.bedtime_display = QLabel()
        self.bedTimeText = "NONE"
        self.displayBedtime = self.bedTimeText
        # This code sets the "Bedtime" by finding the bedtime task, and setting the bedtime timer label to that time
        for task in self.todo_list:
            if task.task_type == TaskType.BEDTIME:
                if task.due_by:
                    self.displayBedtime = task.due_by
                    self.bedtime_display.setText(self.displayBedtime)

        # This is where the Klaus feelings are updated, and the color of the timer_account is set.
        # It works by calculating the ratio of work time (timer accounted - current time) and leisure time
        # (bed time - timer accounted)
        self.update_feeling()

        # This clears the buttons next to each task like the checkbox, play_buttons etc. to avoid duplicates on refresh
        widgets = [self.task_labels, self.check_buttons, self.x_buttons, self.play_buttons, self.timer_lock_in_buttons,
                   self.cancel_buttons, self.minutes_remaining, self.gear_buttons]
        for widget_list in widgets:
            for widget in widget_list:
                if widget is not None:
                    self.layout.removeWidget(widget)
                    widget.deleteLater()
            widget_list.clear()

        # This iterates through the todolist, and draws each task as a horizontal box
        self.task_row_creator()

        if hasattr(self, 'hbox2'):
            index = self.layout.indexOf(self.hbox2)
            layout = self.layout.takeAt(index)
            self.clear_layout(layout)
            self.sub_hbox2 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()

        # Back Button
        self.back_button = QPushButton('Back', self)
        self.back_button.clicked.connect(self.go_back)
        self.hbox2.addWidget(self.back_button)

        # Quick Sort Button
        self.quick_sort_button = QPushButton('Chronological Sort', self)
        self.quick_sort_button.clicked.connect(self.quick_sort)
        self.hbox2.addWidget(self.quick_sort_button)

        # Add List Button
        self.add_list_button = QPushButton('Add a List', self)
        self.add_list_button.clicked.connect(self.open_add_list_window)
        self.hbox2.addWidget(self.add_list_button)

        # Add Task Button
        self.add_task_button = QPushButton('Add Task', self)
        self.add_task_button.clicked.connect(self.open_add_task_window)
        self.hbox2.addWidget(self.add_task_button)

        # Create new QVBoxLayout if it doesn't exist.
        # This QVBoxLayout will be our main layout.
        if not hasattr(self, 'main_layout'):
            self.main_layout = QVBoxLayout()
            self.main_layout.addLayout(self.layout)  # add the previous layout

            self.main_layout.addStretch(1)  # add stretch
            self.main_layout.addLayout(self.hbox2)  # add the hbox2 layout at the end
            self.setLayout(self.main_layout)  # set the new QVBoxLayout as the main layout

        else:  # if main_layout already exists, just update the existing layouts.
            self.layout.update()
            self.hbox2.update()

    # Below are Function Defintions for the t0do window
    # [Group 1] This group of functions help draw the window

    # The functions task_row_creator, create_task_label, create_button draws the task rows which are horizontal
    # rectangles that include the task name and their buttons
    def task_row_creator(self):
        for task in self.todo_list:
            hbox = QHBoxLayout()
            task_label = self.create_task_label(task)
            hbox.addWidget(task_label)

            hbox.addStretch(1)  # Add stretch factor to push the content to the left


            if task.task_type == TaskType.TIMER:
                minutesRemaining = QLabel("Minutes Remaining: {}".format(str(task.duration // 60)))
                hbox.addWidget(minutesRemaining)
                self.minutes_remaining.append(minutesRemaining)
            elif task.task_type == TaskType.SUSTAIN:
                # TODO time calculation for sustain
                minutesRemaining = QLabel("Minutes Remaining: -1")
                hbox.addWidget(minutesRemaining)
                self.minutes_remaining.append(minutesRemaining)
            else:
                self.minutes_remaining.append(None)

            if task.task_type == TaskType.TIMER:
                play_button = self.create_button("\u25B6", "green", 65, self.handle_play_click)
                hbox.addWidget(play_button)
                self.play_buttons.append(play_button)
                timer_lock_in_button = self.create_button("L", "gray", 35, self.handle_timer_lock_in)
                hbox.addWidget(timer_lock_in_button)
                self.timer_lock_in_buttons.append(timer_lock_in_button)

            else:
                self.play_buttons.append(None)
                self.timer_lock_in_buttons.append(None)

            if task.task_type == TaskType.ACTIVE:
                check_button = self.create_button("\u2713", "green", 35, self.handle_check_click)
                hbox.addWidget(check_button)
                self.check_buttons.append(check_button)
            else:
                self.check_buttons.append(None)

            gear_button = self.create_button("\u2699", "gray", 35, self.handle_edit_button)
            hbox.addWidget(gear_button)
            self.gear_buttons.append(gear_button)

            if not self.settings.lock_in and not task.lock_in:
                cancel_button = self.create_button("⨺", "yellow", 35, self.handle_cancel_button)
                hbox.addWidget(cancel_button)
                self.cancel_buttons.append(cancel_button)
            else:
                cancel_button = self.create_button("⨺", "gray", 35, self.handle_cancel_button)
                hbox.addWidget(cancel_button)
                self.cancel_buttons.append(cancel_button)

            x_button_color = "blue" if task.task_type == TaskType.BEDTIME else "red"
            x_button = self.create_button("\u2715", x_button_color, 35, self.handle_x_click)
            hbox.addWidget(x_button)
            self.x_buttons.append(x_button)

            self.layout.addLayout(hbox)
            self.task_labels.append(task_label)

    def create_task_label(self, task):
        task_label = QLabel(task.task_name + "(" + task.due_by + ")", self)
        if task.task_status == TaskStatus.FAILED:
            task_label.setText("<s>" + task_label.text() + "</s>")
            task_label.setStyleSheet("color: red")
        elif task.task_status == TaskStatus.PASSED:
            task_label.setText("<s>" + task_label.text() + "</s>")
            task_label.setStyleSheet("color: green")
        task_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        return task_label

    def create_button(self, text, color, width, handler):
        button = QPushButton(text, self)
        button.setStyleSheet("background-color: " + color)
        button.setFixedWidth(width)
        button.clicked.connect(handler)
        return button


    # This function is where the timers horizontal layout is created, and establishes Klaus's mood
    def update_feeling(self):
        if self.displayBedtime != self.bedTimeText:
            bedtime_datetime = datetime.strptime(self.displayBedtime, "%I:%M %p")
            bedtime_minutes = bedtime_datetime.hour * 60 + bedtime_datetime.minute

            current_time = self.current_time_display.text()
            timer_accounted_time = self.timer_accounted_time_display.text()

            timer_accounted_time_datetime = datetime.strptime(timer_accounted_time, "%I:%M:%S %p")
            current_time_datetime = datetime.strptime(current_time, "%I:%M:%S %p")

            settingTimeMinutes = 60 * self.settings.daily_start_time.hour() + self.settings.daily_start_time.minute()
            addBias = 1440 - settingTimeMinutes

            timer_accounted_time_minutes = timer_accounted_time_datetime.hour * 60 + timer_accounted_time_datetime.minute
            current_time_minutes = current_time_datetime.hour * 60 + current_time_datetime.minute
            bedtime_minutes = bedtime_minutes

            if timer_accounted_time_minutes < settingTimeMinutes:
                timer_accounted_time_minutes = timer_accounted_time_minutes + addBias
            else:
                timer_accounted_time_minutes = timer_accounted_time_minutes - (1440 - addBias)
            if current_time_minutes < settingTimeMinutes:
                current_time_minutes = current_time_minutes + addBias
            else:
                current_time_minutes = current_time_minutes - (1440 - addBias)
            if bedtime_minutes < settingTimeMinutes:
                bedtime_minutes = bedtime_minutes + addBias
            else:
                bedtime_minutes = bedtime_minutes - (1440 - addBias)

            bed_timer_difference = bedtime_minutes - timer_accounted_time_minutes
            work_time_difference = timer_accounted_time_minutes - current_time_minutes
            if work_time_difference == 0:
                work_time_difference = .01

            evalDiff = bed_timer_difference / work_time_difference
            if evalDiff <= 0:
                self.timer_accounted_time_label.setText("<s>" + self.timer_accounted_time_label.text() + "</s>")
                self.timer_accounted_time_label.setStyleSheet("color: red;")

            elif 0 <= evalDiff <= 0.099:
                self.timer_accounted_time_label.setStyleSheet("color: red;")
                self.settings.klaus_state = KlausFeeling.VIOLENT
            elif 0.1 <= evalDiff <= 0.2499:
                self.timer_accounted_time_label.setStyleSheet("color: orange;")
                self.settings.klaus_state = KlausFeeling.ANGRY
            elif 0.25 <= evalDiff <= 0.5:
                self.timer_accounted_time_label.setStyleSheet("color: yellow;")
                self.settings.klaus_state = KlausFeeling.ANNOYED
            elif 0.5 <= evalDiff <= 1:
                self.timer_accounted_time_label.setStyleSheet("color: green;")
                self.settings.klaus_state = KlausFeeling.HAPPY
            else:
                self.timer_accounted_time_label.setStyleSheet("color: purple;")
                self.settings.klaus_state = KlausFeeling.HAPPY
        else:
            self.bedtime_display.setStyleSheet("color: red")
            self.bedtime_display.setText(self.bedTimeText)

        self.hlayout.addWidget(self.current_time_label)
        self.hlayout.addWidget(self.current_time_display)
        # Add a spacer to separate the current time and the timer accounted time
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayout.addItem(self.spacer)
        self.hlayout.addWidget(self.timer_accounted_time_label)
        self.hlayout.addWidget(self.timer_accounted_time_display)
        # Add a spacer to separate the current time and the timer accounted time
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.hlayout.addItem(self.spacer)
        self.hlayout.addWidget(self.bedtime_label)
        self.hlayout.addWidget(self.bedtime_display)

        # Set a timer to update the current time and timer accounted time labels every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCurrentTime)
        self.timer.timeout.connect(self.updateTimerAccountedTime)
        self.timer.start(1000)  # Update the time every 1000 milliseconds (1 second)
        self.layout.addLayout(self.hlayout)

    # [Group 2] This group is where the Timer Threads are handled
    def update_duration(self, task, time_remaining):
        index = self.todo_list.index(task)
        self.todo_list[index].duration = time_remaining
        minute_remaining = self.minutes_remaining[index]
        minute_remaining.setText(
            "Time Left " + str(time_remaining // 3600).zfill(2) + ":" + str((time_remaining % 3600) // 60).zfill(
                2) + ":" + str(time_remaining % 60).zfill(2))
        if (time_remaining == 0):
            task.task_status = TaskStatus.PASSED
            task_label = self.task_labels[index]
            task_label.setStyleSheet("color: green;")
            task_label.setText("<s>" + task_label.text() + "</s>")
            toast = Notification(app_id="Klaus",
                                 title="Reminder",
                                 msg="The timer for " + task.task_name + " is over")
            toast.show()

    def updateCurrentTime(self):
        current_time = QTime.currentTime()
        time_str = current_time.toString("hh:mm:ss ap")

        self.current_time_display.setText(time_str)

    def updateTimerAccountedTime(self):
        runningTime = 0
        hasPlay = False
        for task in self.todo_list:
            if task.task_type == TaskType.TIMER:
                runningTime = runningTime + task.duration
                if task.task_status == TaskStatus.PLAYING:
                    hasPlay = True
        current_time = QTime.currentTime().addSecs(runningTime)
        time_str = current_time.toString("hh:mm:ss ap")
        if hasPlay == False and self.settings.enable_dialogue_reminder_window:
            if self.settings.klaus_state == KlausFeeling.ANNOYED:
                if random.random() < .0001:
                    dialog = ReminderPopUp(self.settings.klaus_state, self)  # Use the main window as the parent
                    dialog.exec_()
            elif self.settings.klaus_state == KlausFeeling.ANGRY:
                if random.random() < .0005:
                    for i in range(3):
                        dialog = ReminderPopUp(self.settings.klaus_state, self)  # Use the main window as the parent
                        dialog.exec_()
            elif self.settings.klaus_state == KlausFeeling.VIOLENT:
                if random.random() < .002:
                    for i in range(5):
                        dialog = ReminderPopUp(self.settings.klaus_state, self)  # Use the main window as the parent
                        dialog.exec_()

        self.timer_accounted_time_display.setText(time_str)

    # Group 3 Button Handle Functionality
    # Below Title Button Functionality
    def refresh_save(self):
        self.parent().show_todolist()
        self.parent().repaint()
        self.parent().update()
        print("Saved and refreshed")
        # Saving the task list to a file
        todoData = {"Tasks": self.todo_list, "Date": datetime.now().date()}

        with open(pickleDirectory + "todo_list.pickle", "wb") as f:
            pickle.dump(todoData, f)
            f.flush()

    def lockIn(self):
        dialog = LockInPopUp(self)  # Use the main window as the parent
        dialog.exec_()

    def handle_memo_button(self):
        dialog = MemoPopUp(self)
        dialog.exec_()

    def handle_calendar_button(self):
        dialog = CalendarPopUp()
        dialog.exec()
    def handle_streak_button(self):
        dialog = StreakPopUp(self)
        dialog.exec_()


    # Task Button Functionality
    def handle_check_click(self):
        sender = self.sender()
        index = self.check_buttons.index(sender)
        task = self.todo_list[index]
        task.task_status = TaskStatus.PASSED
        task_label = self.task_labels[index]
        task_label.setStyleSheet("color: green;")
        task_label.setText("<s>" + task_label.text() + "</s>")
        update_file(self)


    def handle_x_click(self):
        sender = self.sender()
        index = self.x_buttons.index(sender)
        task = self.todo_list[index]
        task.task_status = TaskStatus.FAILED
        task_label = self.task_labels[index]
        task_label.setStyleSheet("color: red;")
        task_label.setText("<s>" + task_label.text() + "</s>")
        update_file(self)

    def handle_play_click(self):
        sender = self.sender()
        index = self.play_buttons.index(sender)
        task = self.todo_list[index]
        if sender.text() == "\u25B6":  # play symbol
            sender.setText("\u23F8")  # pause symbol
            if task.lock_in:
                sender.setStyleSheet("background-color: #ff0000")
            task.task_status = TaskStatus.PLAYING
            self.timer_thread = TimerThread(task, self)
            self.timer_thread.timer_signal.connect(lambda x: self.update_duration(task, x))
            timer_set = False

            # Implements block list for play button
            for filename in os.listdir(pickleDirectory):
                chosen_pickle = makePath(pickleDirectory, filename)
                with open(chosen_pickle, "rb") as file:
                    data = pickle.load(file)
                if data["type"] == "APPLIST":
                    if data["status"] == "TIMER":
                        if timer_set:
                            data["status"] = "INACTIVE"
                        else:
                            timer_set = True

                    if task.app_block_list == filename:
                        data["status"] = "TIMER"
                        self.block_list[0][2] = data["entries"]
                        timer_set = True

                    with open(chosen_pickle, "wb") as file:
                        pickle.dump(data, file)

                if filename.endswith("WEBLIST.pickle"):
                    chosen_pickle = makePath(pickleDirectory, filename)
                    with open(chosen_pickle, "rb") as file:
                        data = pickle.load(file)
                    if data["type"] == "WEBLIST":
                        if data["status"] == "TIMER":
                            if timer_set:
                                data["status"] = "INACTIVE"
                            else:
                                timer_set = True
                        if task.web_block_list == filename:
                            data["status"] = "TIMER"
                            self.block_list[1][0] = data["entries"]
                            timer_set = True

                        with open(chosen_pickle, "wb") as file:
                            pickle.dump(data, file)
            self.timer_thread.start()
        else:
            if not task.lock_in:
                sender.setText("\u25B6")  # play symbol
                task.task_status = TaskStatus.PENDING
                if self.timer_thread is not None:
                    self.timer_thread.stop()  # stop the thread
                    self.timer_thread.wait()  # wait for the thread to finish
                    self.timer_thread.timer_signal.disconnect()
                    self.timer_thread.quit()
                    del self.timer_thread
                    self.timer_thread = None
                timer_set = False
                for filename in os.listdir(pickleDirectory):
                    chosen_pickle = makePath(pickleDirectory, filename)
                    with open(chosen_pickle, "rb") as file:
                        data = pickle.load(file)
                    if data["type"] == "APPLIST":

                        if data["status"] == "TIMER":
                            if timer_set:
                                data["status"] = "INACTIVE"
                            else:
                                timer_set = True

                        if task.app_block_list == filename:
                            data["status"] = "INACTIVE"
                            self.block_list[0][2] = []
                            timer_set = True

                        with open(chosen_pickle, "wb") as file:
                            pickle.dump(data, file)

                    chosen_pickle = makePath(pickleDirectory, filename)
                    with open(chosen_pickle, "rb") as file:
                        data = pickle.load(file)
                    if data["type"] == "WEBLIST":
                        if data["status"] == "TIMER":
                            if timer_set:
                                data["status"] = "INACTIVE"
                            else:
                                timer_set = True

                        if task.web_block_list == filename:
                            data["status"] = "INACTIVE"
                            self.block_list[1][0] = []
                            timer_set = True

                        with open(chosen_pickle, "wb") as file:
                            pickle.dump(data, file)

        if task.web_block_list != "None":
            automate_browser(self.block_list, self.settings)

    def handle_timer_lock_in(self):
        sender = self.sender()
        index = self.timer_lock_in_buttons.index(sender)
        task = self.todo_list[index]
        task.lock_in = True
        self.refresh_save()

    def handle_edit_button(self):
        sender = self.sender()
        index = self.gear_buttons.index(sender)
        self.add_task_window = AddTaskWindow(self, self.todo_list_archive, self.todo_list, self.block_list,
                                             self.settings, index)
        self.add_task_window.show()
        pass

    def handle_cancel_button(self):
        sender = self.sender()
        index = self.cancel_buttons.index(sender)
        task = self.todo_list[index]
        if not self.settings.lock_in and not task.lock_in:
            sender = self.sender()
            index = self.cancel_buttons.index(sender)
            try:
                if self.todo_list[index].task_type == TaskType.TIMER and self.timer_thread is not None:
                    self.timer_thread.timer_signal.disconnect(lambda x: self.update_duration(self.todo_list[index], x))
                    self.timer_thread.stop()  # stop the thread
                    self.timer_thread.wait()  # wait for the thread to finish
                    self.timer_thread.timer_signal.disconnect()
                    self.timer_thread.quit()
                    # self.todo_list[index].timer_thread = None
                    del self.timer_thread

            except Exception as e:
                print(f"An exception occurred while stopping the timer thread: {e}")

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
            update_file(self)
            self.parent().show_todolist()

    # Bottom Row Buttons Functionality
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
                dt = datetime.strptime(task.due_by, date_format)
                return dt
            elif task.task_type == TaskType.BEDTIME:
                date_format = "%I:%M %p"
                dt = datetime.strptime(task.due_by, date_format)
                return dt
            else:
                return float('inf')

        self.todo_list = sorted(self.todo_list, key=task_key)
        self.initUI()

    def go_back(self):
        sender = self.sender()
        for task in self.todo_list:
            if task.task_type == TaskType.TIMER:
                try:
                    if self.timer_thread is not None:
                        self.timer_thread.stop()  # stop the thread
                        self.timer_thread.wait()  # wait for the thread to finish
                        self.timer_thread.timer_signal.disconnect()
                        self.timer_thread.quit()
                        # self.task.timer_thread = None
                        del self.timer_thread

                except Exception as e:
                    print(f"An exception occurred while stopping the timer thread: {e}")
        self.parent().initUI()

    # Open Other Windows
    def open_add_task_window(self):
        self.add_task_window = AddTaskWindow(self, self.todo_list_archive, self.todo_list, self.block_list,
                                             self.settings, -1)
        self.add_task_window.show()

    def open_add_list_window(self):
        self.add_list_window = QuickListAddWindow(self, self.todo_list)
        self.add_list_window.show()



    # [Group 4] Redundancy Funcitons. Functionality you'll use a lot so you just have it a simple function

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    sub_layout = item.layout()
                    if sub_layout is not None:
                        sub_layout.deleteLater()
            layout.deleteLater()
