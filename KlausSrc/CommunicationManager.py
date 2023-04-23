# # !/usr/bin/env -S python -u
#THE ABOVE LINE CREATES SO MANY PROBLEMS... FIGURE OUT HOW TO FIX THIS EVENTUALLY

import struct
import sys
import threading
import queue
import json
from HelperFunctions import createWebsiteBlocklistFromPickles, sendMessage, sendBlocklist, openKlausInstance, MESSAGE_CODES, setGlobalVar

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

# Thread that reads messages from the webapp.
def read_thread_func(aqueue):
  while True:
    # Read the message length (first 4 bytes).
    rawLength = sys.stdin.buffer.read(4)

    if len(rawLength) == 0:
      if aqueue:
        aqueue.put(None)
      sys.exit(0)

    # Unpack message length as 4 byte integer.
    messageLength = struct.unpack('@I', rawLength)[0]

    # Read the text (JSON object) of the message.
    text = json.loads(sys.stdin.buffer.read(messageLength).decode('utf-8'))

    if aqueue:
      aqueue.put(text)
    else:
      # In headless mode just send an echo message back.
      sendMessage('{"echo": %s}' % text)

if tkinter:
  class NativeMessagingWindow(tkinter.Frame):
    def __init__(self, aqueue):
      self.aqueue = aqueue

      tkinter.Frame.__init__(self)
      self.pack()

      self.text = tkinter.Text(self)
      self.text.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
      self.text.config(state=tkinter.DISABLED, height=10, width=40)

      self.messageContent = tkinter.StringVar()
      self.sendEntry = tkinter.Entry(self, textvariable=self.messageContent)
      self.sendEntry.grid(row=1, column=0, padx=10, pady=10)

      self.sendButton = tkinter.Button(self, text="Send", command=self.onSend)
      self.sendButton.grid(row=1, column=1, padx=10, pady=10)

      self.after(100, self.processMessages)

      sendMessage(MESSAGE_CODES.get("COMM_MANAGER_OPENED_MESSAGE"))

      # openKlausInstance()

    def processMessages(self):
      while not self.aqueue.empty():
        message = self.aqueue.get_nowait()

        if message == None:
          self.quit()
          return

        if message == "hello":
            # sendMessage(f"Message: {message}")
          sendMessage("fhjeoaisjdfoj")

        if message == MESSAGE_CODES.get("REQUEST_BLOCKLIST_MESSAGE"):
            self.log(createWebsiteBlocklistFromPickles())
            sendBlocklist()

        if message == MESSAGE_CODES.get("ENABLE_BLOCKLIST_SUCCESSS_MESSAGE"):
            pass

        if MESSAGE_CODES.get("GET_EXTENSION_ID") in message:
            id = message.replace(MESSAGE_CODES.get("GET_EXTENSION_ID") + ":", "")
            setGlobalVar("EXTENSION_ID", id)

        self.log(f"Received {message}")

      self.after(100, self.processMessages)

    def onSend(self):
      text = '{"text": "' + self.messageContent.get() + '"}'
      self.log('Sending %s' % text)
      try:
        sendMessage(text)
      except IOError:
        tkinter.messagebox.showinfo('Native Messaging Example',
                              'Failed to send message.')
        sys.exit(1)

    def log(self, message):
      self.text.config(state=tkinter.NORMAL)
      self.text.insert(tkinter.END, str(message) + "\n")
      self.text.config(state=tkinter.DISABLED)

def Main():
  if not tkinter:
    sendMessage('"Tkinter python module wasn\'t found. Running in headless ' +
                 'mode. Please consider installing Tkinter."')
    read_thread_func(None)
    sys.exit(0)

  aqueue = queue.Queue()

  main_window = NativeMessagingWindow(aqueue)
  main_window.master.title('Klaus Communication Manager')

  thread = threading.Thread(target=read_thread_func, args=(aqueue,))
  thread.daemon = True
  thread.start()

  main_window.mainloop()

  sys.exit(0)


if __name__ == '__main__':
  Main()