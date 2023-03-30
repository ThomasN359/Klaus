#!/usr/bin/env -S python3 -u

from PyQt5.QtWidgets import *
import threading
from HelperFunctions import *

lock_file = 'parent.lock'

exampleBlocklist = ["reddit", "twitter", "twitch"]

class Box(QWidget):

    def __init__(self):
        super().__init__()
        self.thread()
        self.Button()
        sendMessage(COMM_MANAGER_OPENED_MESSAGE)

    def Button(self):
        # add button
        clear_btn = QPushButton('Send example blocklist', self)
        blockListStr = exampleBlocklist[0] + "\n" + "\n".join(exampleBlocklist[1:])
        clear_btn.clicked.connect(lambda: sendMessage(blockListStr))

        # Set geometry
        self.setGeometry(0, 0, 200, 50)

        # Display QlistWidget
        self.show()

    def thread(self):
        t1 = threading.Thread(target=self.Operation)
        t1.start()

    def Operation(self):
        while True:
            if not checkKlausRunning():
                sendMessage(f"{checkKlausRunning()}")
                runKlaus()

            message = getMessage()

            if message == "hello":
                sendMessage(f"Message: {message}")

            if message == PORT_ESTABLISHED_MESSAGE:
                sendMessage("Port has been successfully established")

            if message == REQUEST_BLOCKLIST_MESSAGE:
                sendBlocklist()

            if message == ENABLE_BLOCKLIST_SUCCESSS_MESSAGE:
                pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Box()
    sys.exit(app.exec())
