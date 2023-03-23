#!/usr/bin/env -S python3 -u

from PyQt5.QtWidgets import *
import threading
#libraries for handling communication
import sys
import json
import struct
import os

lock_file = 'parent.lock'

exampleBlocklist = ["reddit", "twitter", "twitch"]

# Read a message from stdin and decode it.
def getMessage():
    rawLength = sys.stdin.buffer.read(4)
    if len(rawLength) == 0:
        sys.exit(0)
    messageLength = struct.unpack('@I', rawLength)[0]
    message = sys.stdin.buffer.read(messageLength).decode('utf-8')
    return json.loads(message)

# Encode a message for transmission, given its content.
def encodeMessage(messageContent):
    # https://docs.python.org/3/library/json.html#basic-usage
    # To get the most compact JSON representation, you should specify (',', ':') to eliminate whitespace.
    # We want the most compact representation because the browser rejects # messages that exceed 1 MB.
    encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
    encodedLength = struct.pack('@I', len(encodedContent))
    return {'length': encodedLength, 'content': encodedContent}

# Send an encoded message to stdout
def sendMessage(encodedMessage):
    sys.stdout.buffer.write(encodedMessage['length'])
    sys.stdout.buffer.write(encodedMessage['content'])
    sys.stdout.buffer.flush()

def sendBlocklist(message):
    encodedMsg = encodeMessage(message)
    sendMessage(encodedMsg)

def evaluateMasterKlausStatus():
    if os.path.exists(lock_file):
        print("Master Klaus is running")
    else:
        with open(lock_file, 'w') as file: #open lock file in write mode
            file.write(str(os.getpid()))
        os.remove(lock_file)

class Box(QWidget):

    def __init__(self):
        super().__init__()
        self.thread()
        self.Button()

    def Button(self):
        # add button
        clear_btn = QPushButton('Send example blocklist', self)
        blockListStr = exampleBlocklist[0] + "\n" + "\n".join(exampleBlocklist[1:])
        blockListStr = encodeMessage(blockListStr)
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
            message = getMessage()

            if message == "hello":
                sendMessage(encodeMessage(f"Message: {message}"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Box()
    sys.exit(app.exec())
