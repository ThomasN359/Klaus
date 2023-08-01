from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class StartTimerPopUp(QDialog):
    def __init__(self, task_name):
        super().__init__()
        print("Entered Start Timer Pop Up")
        self.task_name = task_name

        # Set up the layout
        layout = QVBoxLayout(self)
        self.setWindowTitle("Start Timer")

        # Add a message label
        message_label = QLabel(f"Task {task_name} will begin now", self)
        layout.addWidget(message_label)

        # Add a button to close the dialog
        close_button = QPushButton("OK", self)
        close_button.clicked.connect(self.start_timer)
        layout.addWidget(close_button)
        print("Exit Start Timer Pop Up")

    def start_timer(self):
        self.close()
        pass

    def closeEvent(self, event):
        self.start_timer()
        event.accept()
