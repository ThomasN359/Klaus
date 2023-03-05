import pickle
from PyQt5.QtWidgets import QLabel
from KlausSrc import *
from Main import *

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

        list_entries_label = QLabel("List Entries:", self)
        self.list_entries_textbox = QTextEdit(self)

        save_button = QPushButton("Save", self)
        save_button.clicked.connect(self.save_list)
        back_button = QPushButton("Back", self)
        back_button.clicked.connect(self.go_back)

        edit_list_label = QLabel("Edit a List:", self)
        self.edit_list_combobox = QComboBox(self)
        self.edit_list_combobox.addItems(["None", "Example List 1", "Example List 2", "Example List 3"])
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_name)
        self.edit_list_combobox.currentTextChanged.connect(self.update_list_content)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(back_button)

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

    def update_list_content(self, list_name):
        try:
            with open(f"{list_name}.pickle", "rb") as f:
                data = pickle.load(f)
                self.list_entries_textbox.setPlainText(" ".join(data["entries"]))
                self.list_type_combobox.setCurrentText(data["status"])
        except FileNotFoundError:
            self.list_entries_textbox.setPlainText("")
            self.list_type_combobox.setCurrentText("")

    def save_list(self):
        list_name = self.list_name_textbox.text()
        list_type = self.list_type_combobox.currentText()
        if (list_type == "Block Apps"):
            list_name = list_name + "APPLIST"
        else:
            list_name = list_name + "WEBLIST"
        list_entries = self.list_entries_textbox.toPlainText()
        entries = list_entries.split(" ")

        data = {
            "status": "INACTIVE",
            "entries": entries
        }

        with open(f"{pickleDirectory}/{list_name}.pickle", "wb") as f:
            pickle.dump(data, f)
            f.flush()

    def go_back(self):
        self.parent().initUI()