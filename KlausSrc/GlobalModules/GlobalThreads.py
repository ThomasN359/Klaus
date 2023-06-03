import datetime
import os
import subprocess
import threading
from datetime import *
import time
from PyQt5.QtCore import QThread, pyqtSignal
from winotify import Notification
from KlausSrc.Utilities.HelperFunctions import decrement_brightness, update_daily_settings
from KlausSrc.Objects.Task import TaskStatus, TaskType



class TimerThread(QThread):
    timer_signal = pyqtSignal(int)
    paused = False

    def __init__(self, task, parent=None):
        super().__init__(parent)
        self.task = task
        self._stop_event = threading.Event()
        if parent is not None:
            parent.destroyed.connect(self.quit)

    def run(self):
        time_remaining = int(self.task.duration)
        while time_remaining > 0 and not self._stop_event.is_set():
            if self.paused:
                time.sleep(1)  # sleep for 1 second
                continue
            self.timer_signal.emit(time_remaining)
            time.sleep(1)  # sleep for 1 second
            time_remaining -= 1
        self.timer_signal.emit(0)

    def stop(self):
        self._stop_event.set()


class BlockThread(QThread):
    def __init__(self, block_lists, parent=None):
        super().__init__(parent)
        self.block_lists = block_lists
        self.finished = pyqtSignal()

    def run(self):
        while True:
            time.sleep(2)
            app_block_lists = []
            app_block_lists.extend(self.block_lists[0][0])
            app_block_lists.extend(self.block_lists[0][1])
            app_block_lists.extend(self.block_lists[0][2])

            for app in app_block_lists:
                print("App: " + app)
                process = os.popen(f'tasklist /fi "imagename eq {app}"').read()
                if app in process:
                    os.system(f'taskkill /f /im {app}')
                    print("App found and executed")
                else:
                    time.sleep(3)
                    print("App not found")

# This thread handles scheduled events. This includes notifications, bedtime shutdown, and screen dimmer
class ScheduleThread(QThread):
    def __init__(self, todo_list, settings, parent=None):
        super().__init__(parent)
        self.todo_list = todo_list
        self.settings = settings
        self.finished = pyqtSignal()

    # This is how scheduled events go such as shutting off your computer or notifications
    def run(self):
        i = 0
        while True:
            i += 1
            current_time = datetime.now().time()
            currentClock = current_time.strftime('%I:%M %p')
            current_hour = current_time.hour
            current_minute = current_time.minute

            if current_hour == self.settings.daily_start_time.hour() and current_minute == self.settings.daily_start_time.minute():
                print("entered loop")
                update_daily_settings(self.settings)


            # Check the time and perform the relevant actions
            # The scheduled events are scheduled by tasks inside your todolist so we will loop through each to see if
            # the current time aligns with any time based events saved into the todo_list
            for task in self.todo_list:
                if (task.task_type == TaskType.ACTIVE
                        or task.task_type == TaskType.TIMER
                        or task.task_type == TaskType.BEDTIME)\
                        and task.task_status == TaskStatus.PENDING:

                    # Loop through reminders to see if it's time for a reminder, if yes, display a notification
                    for reminds in task.reminder:
                        reminderTime = reminds
                        timeComponents = reminderTime.split(":")
                        hours = timeComponents[0].zfill(2)
                        minutes = timeComponents[1].split()[0].zfill(2)
                        reminderTime = "{}:{} {}".format(hours, minutes, timeComponents[1].split()[1])
                        # TODO make a function that converts time
                        if str(currentClock) == str(reminderTime):
                            toast = Notification(app_id="Klaus",
                                                 title="Reminder",
                                                 msg="Reminder to complete the task " + task.task_name)
                            toast.show()

                if task.task_type == TaskType.BEDTIME:
                    originalBedTime = task.due_by
                    timeComponents = originalBedTime.split(":")
                    hours = timeComponents[0].zfill(2)
                    minutes = timeComponents[1].split()[0].zfill(2)
                    originalBedTime = "{}:{} {}".format(hours, minutes, timeComponents[1].split()[1])
                    timeBias = self.settings.daily_start_time.hour() * 60 + self.settings.daily_start_time.minute()

                    dt = datetime.strptime(originalBedTime, '%I:%M %p')
                    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                    bed_time_minutes = (dt - midnight).seconds // 60

                    dt = datetime.strptime(currentClock, '%I:%M %p')
                    midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
                    current_time_minutes = (dt - midnight).seconds // 60

                    # Adjust the time to match your setting start time. Such as if they set 6am to start time,
                    # then 5:59 would be the last minute before the day ends, that way 1am isn't a new day yet.
                    if bed_time_minutes < timeBias:
                        bed_time_minutes = 1440 - (timeBias - bed_time_minutes)
                    else:
                        bed_time_minutes -= timeBias
                    if current_time_minutes < timeBias:
                        current_time_minutes = 1440 - (timeBias - current_time_minutes)
                    else:
                        current_time_minutes -= timeBias
                    # If there is 3 hours left, begin decrementing the screen brightness
                    if 180 > bed_time_minutes - current_time_minutes > 0:
                        if i % 10 == 0:
                            decrement_brightness()
                            print("decremented brightness")
                    if originalBedTime == currentClock:
                        toast = Notification(app_id="Klaus",
                                             title="Reminder",
                                             msg="It's bed time, you have 1 minutes before autoshut off",
                                             duration="long")
                        toast.show()
                        print("Prepare for shutdown in 60 seconds minutes")
                        subprocess.run("shutdown /s /t 60", shell=True)
                        time.sleep(60)
            # Sleep for some time so that the loop isn't executed too often
            time.sleep(3)  # Check every three seconds


#This timer thread should be global and applied regradless of what the window's
#state is currently in
class SharedState:
    def __init__(self):
        self.timer_thread = None

    def set_timer_thread(self, timer_thread):
        self.timer_thread = timer_thread

    def get_timer_thread(self):
        return self.timer_thread


shared_state = SharedState()
def kill_timer_thread2(timer_thread, index):
    timer_thread.stop()  # stop the thread
    timer_thread.wait()  # wait for the thread to finish
    timer_thread.timer_signal.disconnect()
    timer_thread.quit()
    # self.task.timer_thread = None
    del timer_thread