import pickle
from KlausSrc.PopUpWindows.MemoPopUp import MemoPopUp
from KlausSrc.PopUpWindows.LockInPopUp import LockInPopUp
from KlausSrc.PopUpWindows.CalendarPopUp import CalendarPopUp
from KlausSrc.PopUpWindows.SchedulerPopUp import SchedulerPopUp
from KlausSrc.Objects.Task import TaskType, TaskStatus
from KlausSrc.MainWindow.Settings import KlausFeeling
from KlausSrc.GlobalModules.GlobalThreads import TimerThread
from KlausSrc.Utilities.config import pickleDirectory, iconDirectory
import random
import os
from datetime import *
from PyQt5 import QtCore
from winotify import Notification
from PyQt5.QtCore import QTime, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from KlausSrc.PopUpWindows.ReminderPopUpWindow import ReminderPopUp
from KlausSrc.Utilities.HelperFunctions import automate_browser, create_button_with_pixmap
from KlausSrc.PopUpWindows.AddTaskWindow import AddTaskWindow
from KlausSrc.PopUpWindows.AddTaskWindow import update_file
from KlausSrc.PopUpWindows.QuickListAddWindow import QuickListAddWindow
from KlausSrc.Utilities.HelperFunctions import makePath


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
        self.previous_sec = None
        # Clear the horizontal box for the title row to avoid duplicates each refresh
        if hasattr(self, 'title_layout'):
            index = self.layout.indexOf(self.title_layout)
            layout = self.layout.takeAt(index)
            self.clear_layout(layout)

        # Here is where the top horizontal row is made, this includes the Todolist, The date, and arrows to navigate
        label = QLabel(self)
        label.setText(f"{datetime.now().strftime('%Y-%m-%d')} Todo List")
        font = label.font()
        font.setPointSize(20)
        label.setFont(font)
        left_button = QPushButton("←", self)
        right_button = QPushButton("→", self)
        left_button.setFixedSize(40, 30)
        self.title_layout = QHBoxLayout()
        right_button.setFixedSize(40, 30)
        self.title_layout.addStretch(1)
        self.title_layout.addWidget(left_button)
        self.title_layout.addWidget(label)
        self.title_layout.addWidget(right_button)
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
        if self.settings.lock_in:
            pixmap = QPixmap(makePath(iconDirectory, "lock.png"))
        else:
            pixmap = QPixmap(makePath(iconDirectory, "unlock.png"))
        self.lock_button = create_button_with_pixmap(pixmap, (35, 35), self.lockIn)
        self.lock_button.setStyleSheet("background-color: #cfcfcf")  # set gray background color
        self.lock_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Scheduler Button
        pixmap = QPixmap(makePath(iconDirectory, "scheduler.png"))
        self.scheduler_button = create_button_with_pixmap(pixmap, (35, 35), self.handle_scheduler_button)
        self.scheduler_button.setStyleSheet("background-color: #e24545")  # set gray background color
        self.scheduler_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Memo Button
        pixmap = QPixmap(makePath(iconDirectory, "memo.png"))
        self.memo_button = create_button_with_pixmap(pixmap, (35, 35), self.handle_memo_button)
        self.memo_button.setStyleSheet("background-color: #ffb200")  # set gray background color
        self.memo_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Refresh Button
        pixmap = QPixmap(makePath(iconDirectory, "refresh_icon.png"))
        self.refresh_button = create_button_with_pixmap(pixmap, (35, 35), self.refresh_save)
        self.refresh_button.setStyleSheet("background-color: #00ff00")  # set gray background color
        self.refresh_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        # Calendar Button
        pixmap = QPixmap(makePath(iconDirectory, "calender.png"))
        self.calendar_button = create_button_with_pixmap(pixmap, (35, 35), self.handle_calendar_button)
        self.calendar_button.setStyleSheet("background-color: #00ffff")  # set gray background color
        self.calendar_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels

        pixmap = QPixmap(makePath(iconDirectory, "sort.png"))
        self.sort_button = create_button_with_pixmap(pixmap, (35,35), self.quick_sort)
        self.sort_button.setStyleSheet("background-color: #0000ff")
        self.sort_button.setFixedSize(45, 45)

        pixmap = QPixmap(makePath(iconDirectory, "list_add.png"))
        self.list_add_button = create_button_with_pixmap(pixmap, (35,35), self.open_add_list_window)
        self.list_add_button.setStyleSheet("background-color: #C8A2C8")
        self.list_add_button.setFixedSize(45, 45)

        self.sub_title_layout.addStretch(1)
        self.sub_title_layout.addWidget(self.refresh_button)
        self.sub_title_layout.addWidget(self.memo_button)
        self.sub_title_layout.addWidget(self.lock_button)
        self.sub_title_layout.addWidget(self.scheduler_button)
        self.sub_title_layout.addWidget(self.sort_button)
        self.sub_title_layout.addWidget(self.list_add_button)
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
        pixmap = (makePath(iconDirectory, "back_arrow.png"))
        self.back_button = create_button_with_pixmap(pixmap, (100,100), self.go_back)
        self.back_button.setStyleSheet("background-color: transparent; border: none;")
        self.hbox2.addWidget(self.back_button)

        # Add Task Button
        pixmap = (makePath(iconDirectory, "add.png"))
        self.add_task_button = create_button_with_pixmap(pixmap, (100,100), self.open_add_task_window)
        self.add_task_button.setStyleSheet("background-color: transparent; border: none;")
        self.hbox2.addStretch(1)
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
                if task.lock_in and task.task_status == TaskStatus.PLAYING:
                    play_button = self.create_button("\u23F8", "red", 65, self.handle_play_click)
                else:
                    play_button = self.create_button("\u25B6", "green", 65, self.handle_play_click)
                hbox.addWidget(play_button)
                self.play_buttons.append(play_button)

                if task.lock_in:
                    pixmap = QPixmap(makePath(iconDirectory, "lock.png"))
                else:
                    pixmap = QPixmap(makePath(iconDirectory, "unlock.png"))
                timer_lock_in_button = create_button_with_pixmap(pixmap, (30, 30), self.handle_timer_lock_in)
                timer_lock_in_button.setStyleSheet("background-color: #cfcfcf")  # set gray background color
                timer_lock_in_button.setFixedSize(45, 45)  # set fixed size of 30x30 pixels
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

        # Ensure the time only decreases
        current_sec = current_time.second()
        if self.previous_sec is not None and current_sec > self.previous_sec:
            current_time = current_time.addSecs(-1)
            time_str = current_time.toString("hh:mm:ss ap")
        self.previous_sec = current_sec

        if not hasPlay and self.settings.enable_dialogue_reminder_window:
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
        self.initUI()
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
        dialog = CalendarPopUp(self.settings, self.todo_list)
        dialog.exec()

    def handle_scheduler_button(self):
        dialog = SchedulerPopUp(self.settings, self.todo_list)
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
                    self.kill_timer_thread(index)

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
        index = -1
        for task in self.todo_list:
            index += 1
            if task.task_type == TaskType.TIMER:
                try:
                    self.kill_timer_thread(index)
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

    # Timer task utilize a global thread. When we pause the timer we kill the thread. We can then make a new thread
    # and attach it to the task if it becomes unpaused. Call this to kill the thread to prevent bugs when leaving
    # the timer task's count down display
    def kill_timer_thread(self, index):
        self.timer_thread.stop()  # stop the thread
        self.timer_thread.wait()  # wait for the thread to finish
        self.timer_thread.timer_signal.disconnect()
        self.timer_thread.quit()
        # self.task.timer_thread = None
        del self.timer_thread