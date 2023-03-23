import os
import pickle
from PyQt5.QtWidgets import QPushButton, QLabel, QDialog, QVBoxLayout, QLineEdit, QComboBox
from config import pickleDirectory
from HelperFunctions import makePath

class QuickListAddWindow(QDialog):
    def __init__(self, parent, todo_list):
        self.todo_list = todo_list
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 500, 300)
        self.setWindowTitle("Quick Add")

        self.layout = QVBoxLayout()

        # Name Your List Label
        self.name_label = QLabel("Name your current list to quick save it")
        self.layout.addWidget(self.name_label)

        # Name Task
        self.name_textbox = QLineEdit()
        self.layout.addWidget(self.name_textbox)

        # Quick Save Button
        self.quick_save_button = QPushButton("Quick Save")
        self.quick_save_button.clicked.connect(self.quick_save)
        self.layout.addWidget(self.quick_save_button)

        self.choose_label = QLabel("Choose a list to quick add")
        self.layout.addWidget(self.choose_label)

        # Display the files from your file directory to display in the drop down "choose" box
        self.choose_combobox = QComboBox()

        for filename in os.listdir(pickleDirectory):
            with open(makePath(pickleDirectory, filename), "rb") as f:
                data = pickle.load(f)
            if data["type"] == "QUICK_LIST":
                self.choose_combobox.addItem(filename.replace(".pickle", ""))

        self.layout.addWidget(self.choose_combobox)

        # Quick Add
        self.quick_add_button = QPushButton("Quick Add")
        self.quick_add_button.clicked.connect(self.quick_add)
        self.layout.addWidget(self.quick_add_button)

        self.setLayout(self.layout)

    # This function connects to the Quick Save button and quick saves by dumping it into a file on your computer
    def quick_save(self):
        pickle_file = makePath(pickleDirectory, self.name_textbox.text()+".pickle")
        if not os.path.exists(pickleDirectory):
            os.makedirs(pickleDirectory)

        data = {"task_list": self.todo_list, "type": "QUICK_LIST"}

        with open(pickle_file, "wb") as f:
            pickle.dump(data, f)

    # This function connects to the quick add button
    def quick_add(self):
        chosen_pickle = makePath(pickleDirectory, self.choose_combobox.currentText() + ".pickle")
        with open(chosen_pickle, "rb") as f:
            data = pickle.load(f)
        self.todo_list.extend(data["task_list"])
        self.parent().initUI()
        self.close()
        self.parent().repaint()
        self.parent().update()