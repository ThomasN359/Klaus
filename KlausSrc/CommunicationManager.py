# # !/usr/bin/env -S python -u
# THE ABOVE LINE CREATES SO MANY PROBLEMS... FIGURE OUT HOW TO FIX THIS EVENTUALLY

import struct
import sys
import threading
import queue
import json
from HelperFunctions import createWebsiteBlocklistFromPickles, sendMessage, sendBlocklist, MESSAGE_CODES, setGlobalVar, \
    toCommManagerQueue, toNativeKlausQueue, runKlaus

exampleBlocklist = ["reddit", "twitter", "twitch"]
extensionID = ""

try:
    import tkinter
    import tkinter.messagebox
except ImportError:
    tkinter = None

# On Windows, the default I/O mode is O_TEXT. Set this to O_BINARY
# to avoid unwanted modifications of the input/output streams.
if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)


# Thread that reads messages from the extension.
def read_ext_thread_func(extensionCommQueue, closeEvent):
    while True:
        if closeEvent.is_set():
            print("Closing read thread")
            sys.exit(0)

        # Read the message length (first 4 bytes).
        rawLength = sys.stdin.buffer.read(4)

        if len(rawLength) == 0:
            if extensionCommQueue:
                extensionCommQueue.put(None)
            sys.exit(0)

        # Unpack message length as 4 byte integer.
        messageLength = struct.unpack('@I', rawLength)[0]

        # Read the text (JSON object) of the message.
        text = json.loads(sys.stdin.buffer.read(messageLength).decode('utf-8'))

        if extensionCommQueue:
            extensionCommQueue.put(text)
        else:
            # In headless mode just send an echo message back.
            sendMessage('{"echo": %s}' % text)


if tkinter:
    class NativeMessagingWindow(tkinter.Frame):
        def __init__(self, extensionCommQueue, toCommManagerQueue, closeEvent):
            self.extensionCommQueue = extensionCommQueue
            self.toCommManagerQueue = toCommManagerQueue
            self.closeEvent = closeEvent

            self.root = tkinter.Tk()
            self.root.protocol("WM_DELETE_WINDOW", self.onClose)
            self.root.title('Klaus Communication Manager')

            tkinter.Frame.__init__(self)
            self.pack()

            self.text = tkinter.Text(self)
            self.text.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
            self.text.config(state=tkinter.DISABLED, height=10, width=40)

            self.messageContent = tkinter.StringVar()
            self.sendEntry = tkinter.Entry(self, textvariable=self.messageContent)
            self.sendEntry.grid(row=1, column=0, padx=10, pady=10)

            self.sendButton = tkinter.Button(self, text="Send", command=self.onSendToExtension)
            self.sendButton.grid(row=1, column=1, padx=10, pady=10)

            self.after(100, self.processMessagesFromExtension)
            self.after(100, self.processMessagesFromNative)

            sendMessage(MESSAGE_CODES.get("COMM_MANAGER_OPENED_MESSAGE"))

        def processMessagesFromExtension(self):
            while not self.extensionCommQueue.empty():
                message = self.extensionCommQueue.get_nowait()

                if message is None:
                    self.quit()
                    return

                if message == "hello":
                    # sendMessage(f"Message: {message}")
                    sendMessage("hello received")

                if message == MESSAGE_CODES.get("REQUEST_BLOCKLIST_MESSAGE"):
                    self.log(createWebsiteBlocklistFromPickles())
                    sendBlocklist()

                if message == MESSAGE_CODES.get("ENABLE_BLOCKLIST_SUCCESS_MESSAGE"):
                    pass

                if MESSAGE_CODES.get("GET_EXTENSION_ID_MESSAGE") in message:
                    id = message.replace(MESSAGE_CODES.get("GET_EXTENSION_ID_MESSAGE") + ":", "")
                    setGlobalVar("EXTENSION_ID", id)

                if message == MESSAGE_CODES.get("OPEN_KLAUS_MESSAGE"):
                    runKlaus()

                self.log(f"Extension:{message}")

            self.after(100, self.processMessagesFromExtension)

        #  Reads messages from native Klaus queue
        def processMessagesFromNative(self):
            while not self.toCommManagerQueue.empty():
                message = self.toCommManagerQueue.get_nowait()

                if message is None:
                    self.quit()
                    return

                self.log(f"Native:{message}")

            self.after(100, self.processMessagesFromNative)

        def sendMessageToNative(self, msg):
            toNativeKlausQueue.put_nowait(msg)

        def onSendToExtension(self):
            text = '{"text": "' + self.messageContent.get() + '"}'
            self.log('Sending %s' % text)
            try:
                sendMessage(text)
            except IOError:
                tkinter.messagebox.showinfo('Native Messaging Example',
                                            'Failed to send message.')
                sys.exit(1)

        def onClose(self):
            self.closeEvent.set()
            self.root.destroy()

        def log(self, message):
            self.text.config(state=tkinter.NORMAL)
            self.text.insert(tkinter.END, str(message) + "\n")
            self.text.config(state=tkinter.DISABLED)


def Main():
    if not tkinter:
        sendMessage('"Tkinter python module wasn\'t found. Running in headless ' +
                    'mode. Please consider installing Tkinter."')
        read_ext_thread_func(None)
        sys.exit(0)

    runKlaus()

    extensionCommQueue = queue.Queue()

    closeEvent = threading.Event()
    main_window = NativeMessagingWindow(extensionCommQueue, toCommManagerQueue, closeEvent)
    main_window.mainloop()

    thread = threading.Thread(target=read_ext_thread_func, args=(extensionCommQueue, closeEvent,))
    thread.start()
    thread.join()

    sys.exit(0)


if __name__ == '__main__':
    Main()
