import os

from PyQt5.QtWidgets import QPushButton

from KlausSrc import *
from Main import *

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
            if filename.endswith("qs.pickle"):
                self.choose_combobox.addItem(filename.replace("qs.pickle", ""))

        self.layout.addWidget(self.choose_combobox)

        # Quick Add
        self.quick_add_button = QPushButton("Quick Add")
        self.quick_add_button.clicked.connect(self.quick_add)
        self.layout.addWidget(self.quick_add_button)

        self.setLayout(self.layout)

    # This function connects to the Quick Save button and quick saves by dumping it into a file on your computer
    def quick_save(self):
        pickle_file = pickleDirectory + "/" + self.name_textbox.text() + "qs.pickle"
        if not os.path.exists(pickleDirectory):
            os.makedirs(pickleDirectory)

        data = ("Quick Add", self.todo_list)

        with open(pickle_file, "wb") as f:
            pickle.dump(data, f)

    # This function connects to the quick add button
    def quick_add(self):
        chosen_pickle = "Pickles/" + self.choose_combobox.currentText() + "qs.pickle"
        with open(chosen_pickle, "rb") as f:
            data = pickle.load(f)
        self.todo_list.extend(data[1])
        self.parent().initUI()
        self.close()
        self.parent().repaint()
        self.parent().update()