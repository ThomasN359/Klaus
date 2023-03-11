import os
import pickle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QVBoxLayout, QWidget, QLineEdit, QTextEdit, QHBoxLayout
from config import pickleDirectory


class ListCreatorWindow(QWidget):
    def __init__(self, todo_list_archive, todo_list, parent=None):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.initUI()

    def initUI(self):
        label = QLabel("List Creator", self)
        label.setAlignment(Qt.AlignCenter)

        list_name_label = QLabel("List Name:", self)
        self.list_name_textbox = QLineEdit(self)

        list_type_label = QLabel("List Type:", self)
        self.list_type_combobox = QComboBox(self)
        self.list_type_combobox.addItems(["Block Apps", "Block Websites"])
        self.list_type_combobox.currentIndexChanged.connect(self.update_list_UI)

        list_entries_label = QLabel("List Entries:", self)
        self.list_entries_textbox = QTextEdit(self)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_list)
        back_button = QPushButton("Back", self)
        back_button.clicked.connect(self.go_back)
        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.delete)

        edit_list_label = QLabel("Edit a List:", self)
        fileList = ["None"]
        self.edit_list_combobox = QComboBox(self)

        type = ""

        for filename in os.listdir(pickleDirectory):
            filePath = pickleDirectory + "\\" + filename
            try:
                with open(filePath, "rb") as f:
                    data = pickle.load(f)
                    type = data["type"]
            except FileNotFoundError:
                print("File not found")
            if self.list_type_combobox.currentText() == "Block Apps":
                if type == "APPLIST":
                    fileList.append(filename)
            elif self.list_type_combobox.currentText() == "Blocked Websites":
                if type == "WEBLIST":
                    fileList.append(filename)

        self.edit_list_combobox.addItems(fileList)
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_name)
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_content)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(back_button)
        buttons_layout.addWidget(delete_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(label)
        main_layout.addWidget(list_name_label)
        main_layout.addWidget(self.list_name_textbox)
        main_layout.addWidget(edit_list_label)
        main_layout.addWidget(self.edit_list_combobox)
        main_layout.addWidget(list_type_label)
        main_layout.addWidget(self.list_type_combobox)
        main_layout.addWidget(list_entries_label)
        main_layout.addWidget(self.list_entries_textbox)
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def update_list_name(self, list_name):
        self.list_name_textbox.setText(list_name)

    def update_list_UI(self):
        new_index = self.list_type_combobox.currentIndex()
        self.list_type_combobox.setCurrentIndex(new_index)
        print("inward " + str(self.list_type_combobox.currentIndex()))
        fileList = []
        for filename in os.listdir(pickleDirectory):
            filePath = pickleDirectory + "\\" + filename
            try:
                with open(filePath, "rb") as f:
                    data = pickle.load(f)
                    type = data["type"]
            except FileNotFoundError:
                print("File not found")
            if self.list_type_combobox.currentText() == "Block Apps":
                if type == "APPLIST":
                    fileList.append(filename)
            elif self.list_type_combobox.currentText() == "Block Websites":
                if type == "WEBLIST":
                    fileList.append(filename)

        self.edit_list_combobox.clear()
        fileList.insert(0, "None")
        self.edit_list_combobox.addItems(fileList)


    def update_list_content(self, list_name):
        pickle_file = pickleDirectory + "\\" + list_name
        try:
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
                self.list_entries_textbox.setPlainText(" ".join(data["entries"]))
        except FileNotFoundError:
            self.list_entries_textbox.setPlainText("")
            self.list_type_combobox.setCurrentText("")

    def save_list(self):
        list_name = self.list_name_textbox.text()
        list_type = self.list_type_combobox.currentText()
        if list_type == "Block Apps":
            list_name = list_name
        else:
            list_name = list_name
        list_entries = self.list_entries_textbox.toPlainText()
        entries = list_entries.split(" ")

        if self.list_type_combobox.currentText() == "Block Apps":
            pickleType = "APPLIST"
        else:
            pickleType = "WEBLIST"

        data = {
            "status": "INACTIVE",
            "type": pickleType,
            "entries": entries
        }

        filePath = f"{pickleDirectory}\{list_name}.pickle"
        if filePath.endswith(".pickle.pickle"):
            filePath = filePath[:-7]
        with open(filePath, "wb") as f:
            pickle.dump(data, f)
            f.flush()
        self.initUI()

    def go_back(self):
        self.parent().initUI()

    def delete(self):
        if self.list_name_textbox.text() != "":
            filePath = f"{pickleDirectory}\{self.list_name_textbox.text()}.pickle"
            if filePath.endswith(".pickle.pickle"):
                filePath = filePath[:-7]
            os.remove(filePath)
            self.list_name_textbox.setText("")
            self.list_type_combobox.setCurrentIndex(0)
            self.list_entries_textbox.setText("")
        self.initUI()
