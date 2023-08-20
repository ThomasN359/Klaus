import enum
import os
import pickle
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QPushButton, QComboBox, QVBoxLayout, QLineEdit, QTextEdit, QHBoxLayout, \
    QDialog, QDesktopWidget
from KlausSrc.Utilities.config import pickleDirectory
from KlausSrc.Utilities.HelperFunctions import makePath

class ListCreatorPopUp(QDialog):
    def __init__(self, parent, todo_list_archive, todo_list, block_list):
        super().__init__(parent)
        self.todo_list_archive = todo_list_archive
        self.todo_list = todo_list
        self.block_list = block_list
        screen = QDesktopWidget().screenGeometry()
        width = screen.width() // 3  # One-third of the screen width
        height = int(screen.height() * 0.9)

        # Set the window geometry
        self.setGeometry(0, 0, width, height)
        self.initUI()

    def initUI(self):
        label = QLabel("List Creator", self)
        label.setAlignment(Qt.AlignCenter)

        list_name_label = QLabel("List Name:", self)
        self.list_name_textbox = QLineEdit(self)
        self.list_name_textbox.setStyleSheet("QLineEdit { background-color: rgba(255, 255, 255, 128); }")


        list_type_label = QLabel("List Type:", self)
        self.list_type_combobox = QComboBox(self)
        self.list_type_combobox.setStyleSheet("QComboBox{ background-color: rgba(255, 255, 255, 128); }")

        self.list_type_combobox.addItems(["Block Apps", "Block Websites"])
        self.list_type_combobox.currentIndexChanged.connect(self.update_list_UI)


        list_entries_label = QLabel("List Entries:", self)
        self.list_entries_textbox = QTextEdit(self)
        self.list_entries_textbox.setStyleSheet("QTextEdit{ background-color: rgba(255, 255, 255, 128); }")



        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_list)
        delete_button = QPushButton("Delete", self)
        delete_button.clicked.connect(self.delete)

        edit_list_label = QLabel("Edit a List:", self)
        fileList = ["None"]
        self.edit_list_combobox = QComboBox(self)
        self.edit_list_combobox.setStyleSheet("QComboBox { background-color: rgba(255, 255, 255, 128); }")

        if self.list_type_combobox.currentText() == "Block Apps":
            for app_list_name in self.block_list[0].keys():
                fileList.append(app_list_name)
        elif self.list_type_combobox.currentText() == "Blocked Websites":
            for web_list_name in self.block_list[1].keys():
                fileList.append(web_list_name)

        self.edit_list_combobox.addItems(fileList)
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_name)
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_content)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_button)
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
            filePath = makePath(pickleDirectory, filename)
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
        try:
            pickle_file = makePath(pickleDirectory, list_name)
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
                self.list_entries_textbox.setPlainText(" ".join(data["entries"]))
        except FileNotFoundError:
            self.list_entries_textbox.setPlainText("")
            self.list_type_combobox.setCurrentText("")
        except IsADirectoryError:
            pass

    def save_list(self):
        list_name = self.list_name_textbox.text()
        list_entries = self.list_entries_textbox.toPlainText()
        entries = list_entries.split(" ")

        if self.list_type_combobox.currentText() == "Block Apps":
            new_list = {list_name: (entries, self.parent().ListStatus.OFF)}
            self.block_list[0].update(new_list)
        else:
            new_list = {list_name: (entries, self.parent().ListStatus.OFF)}
            self.block_list[1].update(new_list)
        self.save_block_list()



    def save_block_list(self):
        # Saving the task list to a file
        block_list_data = {"Blocklists": self.block_list, "type": "BLOCKLIST"}
        chosenFile = makePath(pickleDirectory, "block_list.pickle")
        with open(chosenFile, "wb") as f:
            print(str(f))
            pickle.dump(block_list_data, f)
            f.flush()

    #TODO MAYBE MAKE A NEW DELETE BUTTON IN NEW BLOCK LIST UI
    def delete(self):
        if self.list_name_textbox.text() != "":
            filePath = makePath(pickleDirectory, self.list_name_textbox.text()+".pickle")
            if filePath.endswith(".pickle.pickle"):
                filePath = filePath[:-7]
            os.remove(filePath)
            self.list_name_textbox.setText("")
            self.list_type_combobox.setCurrentIndex(0)
            self.list_entries_textbox.setText("")
        self.initUI()
