import pickle
from datetime import datetime

from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QLineEdit, QVBoxLayout

from config import pickleDirectory
from HelperFunctions import makePath


class NutritionWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.setGeometry(0, 0, 100, 100)
        self.initUI()

    def initUI(self):
        # Initialize variables
        self.daily_metabolic_rate = 0
        self.net_calories = 0
        self.last_save_time = datetime.now()

        # Load saved data from pickle
        try:
            with open(makePath(pickleDirectory,"net_calories.pickle"), "rb") as f:
                data = pickle.load(f)
                self.last_save_time = data["timestamp"]
                self.net_calories = data["calories"]
                self.daily_metabolic_rate = data["metabolic_rate"]
        except FileNotFoundError:
            pass

        # Create GUI elements
        self.net_calories_label = QLabel("Net Calories: 0")
        self.add_calories_button = QPushButton("Add Calories")
        self.calories_input = QLineEdit()
        self.metabolic_rate_input = QLineEdit()
        self.metabolic_rate_input.setText(str(self.daily_metabolic_rate))
        self.net_pounds_label = QLabel("Net Pounds: 0")
        # Create the "Back" button and connect it to the "go_back" slot
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)

        # Connect button click event to add_calories method
        self.add_calories_button.clicked.connect(self.on_add_calories_clicked)

        # Create timer to update net calories every second
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_net_calories)
        self.timer.start(1000)  # 1000 ms = 1 second

        # Add GUI elements to layout
        layout = QVBoxLayout()
        layout.addWidget(self.net_calories_label)
        layout.addWidget(self.net_pounds_label)
        layout.addWidget(self.calories_input)
        layout.addWidget(self.add_calories_button)
        layout.addWidget(QLabel("Daily Metabolic Rate:"))
        layout.addWidget(self.metabolic_rate_input)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

    def update_net_calories(self):
        # Calculate time elapsed since last update
        now = datetime.now()
        time_elapsed = (now - self.last_save_time).total_seconds()
        self.last_save_time = now

        # Calculate net calories
        net_calories_lost = self.daily_metabolic_rate / 86400  # 86400 seconds in a day
        self.net_calories -= net_calories_lost * time_elapsed

        # Save net calories and metabolic rate to pickle every minute
        if now.second % 12 == 0:
            with open(makePath(pickleDirectory,"net_calories.pickle"), "wb") as f:
                data = {"calories": self.net_calories, "metabolic_rate": self.daily_metabolic_rate, "timestamp": now, "type": "NUTRITION_LIST"}
                pickle.dump(data, f)
        # Calculate net pounds and format as decimal with 4 digits
        net_pounds = self.net_calories / 3500
        net_pounds_formatted = "{:.6f}".format(net_pounds)

        # Format net calories as decimal with 4 digits and update net calories and net pounds labels
        net_calories_formatted = "{:.4f}".format(self.net_calories)
        self.net_calories_label.setText("Net Calories: {}".format(net_calories_formatted))
        self.net_pounds_label.setText("Net Pounds: {}".format(net_pounds_formatted))

    def on_add_calories_clicked(self):
        # Get calories input value and add to net calories
        calories = int(self.calories_input.text())
        self.net_calories += calories

        # Update net calories and net pounds labels
        net_calories_formatted = "{:.4f}".format(self.net_calories)
        self.net_calories_label.setText("Net Calories: {}".format(net_calories_formatted))
        net_pounds = self.net_calories / 3500
        net_pounds_formatted = "{:.4f}".format(net_pounds)
        self.net_pounds_label.setText("Net Pounds: {}".format(net_pounds_formatted))

    def update_metabolic_rate(self, metabolic_rate):
        self.daily_metabolic_rate = metabolic_rate
        self.metabolic_rate_input.setText(str(metabolic_rate))

    def save_stats(self):
        # Save net calories and metabolic rate to pickle
        now = datetime.datetime.now()
        with open(makePath(pickleDirectory,"net_calories.pickle"), "wb") as f:
            data = {"calories": self.net_calories, "metabolic_rate": self.daily_metabolic_rate, "timestamp": now,
                    "type": "NUTRITION_LIST"}
            pickle.dump(data, f)

    def load_stats(self):
        # Load saved data from pickle
        try:
            with open(makePath(pickleDirectory,"net_calories.pickle"), "rb") as f:
                data = pickle.load(f)
                self.last_save_time, self.net_calories, self.daily_metabolic_rate = pickle.load(f)
                self.last_save_time = data["timestamp"]
                self.net_calories = data["calories"]
                self.daily_metabolic_rate = data["metabolic_rate"]
        except FileNotFoundError:
            pass

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            metabolic_rate = int(self.metabolic_rate_input.text())
            self.update_metabolic_rate(metabolic_rate)
        else:
            super().keyPressEvent(event)

    def go_back(self):
        self.parent().initUI()
