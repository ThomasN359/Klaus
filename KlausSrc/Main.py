import sys
import os
dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(dir) #this fixes some weird importing thing when running communicationManager initialized by chrome

import multiprocessing

from KlausSrc.MainWindow.Settings import *
from KlausSrc.MainWindow.TodolistWindow import *
from KlausSrc.MainWindow.HomeScreen import HomeScreen
from KlausSrc.Utilities.HelperFunctions import *
from KlausSrc.Utilities.Singleton import Singleton
from KlausSrc.MainWindow.WindowHolder import WindowHolder

from datetime import *
from PyQt5.QtCore import QTime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *



def main_process():  # TODO FLAG AND LOCK

    # Initialize the starting variables for the program
    settings = Settings()
    todo_list = []
    todo_list_archive = {}
    #the block_lists is a list with two components which are dictionaries. The first dictionary is for weblist,
    #the second dictionary is for applist. Each dictionary contains a string as the list name, and a list.
    block_lists = [{}, {}]
    timeStamp = None

    # Below here, items are loaded and initialized in your system, such as settings, todolist, block list etc.

    # Load in blocklist Pickle
    try:
        with open(makePath(pickleDirectory, "block_list.pickle"), "rb") as f:
            block_list_data = pickle.load(f)
            block_lists = block_list_data["Blocklists"]
            block_type = block_list_data["type"]
    except:
        block_lists = [{},{}]


    # Load in t0dolist archive
    try:
        with open(makePath(pickleDirectory, "todo_list_archive.pickle"), "rb") as f:
            todo_list_archive_data = pickle.load(f)
            todo_list_archive = todo_list_archive_data["Todolists"]

    except:
        # Handle the exception and continue without the data
        todo_list_archive = {}
        pass

    # Load in most recent t0do list
    try:
        with open(makePath(pickleDirectory, "todo_list.pickle"), "rb") as f:
            todoData = pickle.load(f)
            todo_list = todoData["tasks"]
            timeStamp = todoData["date"]

    except:
        # Handle the exception and continue without the data
        todo_list = []
        pass

    try:
        with open(makePath(pickleDirectory, "scheduler.pickle"), "rb") as f:
            schedulerData = pickle.load(f)
            scheduler = schedulerData["scheduler"]
    except:
        days_of_week = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
        scheduler = {day: [] for day in days_of_week}

        with open(makePath(pickleDirectory, 'scheduler.pickle'), 'wb') as f:
            data = {"scheduler": scheduler, "type": "scheduler"}
            pickle.dump(data, f)
            f.flush()

    # Load in settings
    try:
        with open(makePath(pickleDirectory, "settings.pickle"), "rb") as f:
            data = pickle.load(f)
            settings = data["settings"]
    # If there is no settings at all that means it's the first time having settings
    except:
        # Handle the exception and continue without the data
        settings.daily_start_time = QTime(0, 0)
        # First is Brave, second is Chrome, Third is edge. These check which browsers you currently use.
        settings.browsers = [False, True, False]
        settings.klaus_state = KlausFeeling.HAPPY
        settings.enable_dialogue_reminder_window = True
        settings.lock_in = False
        settings.has_daily_update = True

        with open(makePath(pickleDirectory, 'settings.pickle'), 'wb') as f:
            data = {"settings": settings, "type": "SETTINGS"}
            pickle.dump(data, f)
            f.flush()

    # if we are on a new day then continue from here
    if (datetime.now().hour >= settings.daily_start_time.hour() and (
            datetime.now().date() != timeStamp or timeStamp is None) and settings.enable_lock_out):
        settings.has_daily_update = False
        update_daily_settings(settings)
        if len(todo_list) > 0:
            todo_list_archive[timeStamp] = todo_list  # Adjust how we save to the archive
            try:
                with open(makePath(pickleDirectory, 'todo_list_archive.pickle'), "wb") as f:
                    pickle.dump(todo_list_archive, f)
                    f.flush()
            except:
                # Handle the exception and continue without the data
                print("Error loading archive pickle")
                pass
        blockedApps = []
        if settings.browsers[0]:
            blockedApps.append("brave.exe")
        if settings.browsers[1]:
            blockedApps.append("chrome.exe")
        if settings.browsers[2]:
            blockedApps.append("msedge.exe")
        block_lists[0][0] = blockedApps
        todo_list = []  # refresh the todolist because it's a new day

    app = QApplication([])
    font = QFont("Arial", 15)
    app.setFont(font)
    main_window = HomeScreen(todo_list_archive, todo_list, block_lists, settings, scheduler, 1)

    #main_window.show()
    main_window2 = HomeScreen(todo_list_archive, todo_list, block_lists, settings, scheduler, 2)

    main_window3 = WindowHolder(todo_list_archive, todo_list, block_lists, settings, main_window, main_window2)
    main_window3.showMaximized()
    # This handles the schedule things such as notifications
    # main_window.start_scheduling()
    # main_window.start_blocking()

    # Connect close event to handle_close_event
    # main_window.closeEvent = lambda event: handle_close_event(event, flag, lock) #T0DO flag and lock
    # This handles the block list
    sys.exit(app.exec())


def main():
    # Create GUI process
    # event = multiprocessing.Event()
    # lock = multiprocessing.Lock()
    # flag = multiprocessing.Value('i', 1)
    #
    # gui_klaus = multiprocessing.Process(target=main_process, args=(flag, lock))
    # gui_klaus.start()
    #
    # # Wait for GUI to start
    # time.sleep(1)
    #
    # # Create checker process
    # checker_p = multiprocessing.Process(target=checker_process, args=(flag, lock))
    # checker_p.start()
    #
    # # Wait for GUI process to finish
    # gui_klaus.join()
    # main_process(flag, lock)

    with Singleton():
        main_process()


# This is a global function that overrides the normal "X" close button by including the information about respawning
def handle_close_event(flag, lock):
    print("Entered here")
    with lock:
        flag.value = 0


def checker_process(flag, lock):
    while True:
        with lock:
            if flag.value == 1:
                pass
                ("GUI is running" + str(flag.value))
            else:
                print("GUI is closed with value " + str(flag.value))
                # Start a new GUI process if the previous one was closed
                new_gui_p = multiprocessing.Process(target=main_process, args=(flag, lock))
                flag.value = 1
                new_gui_p.start()
        time.sleep(1)


if __name__ == '__main__':
    main()
