import ctypes
import subprocess
import time
import traceback
import os
import atexit
import signal
import sys
import psutil

try:
    import pyautogui
except ImportError:
    pass

import struct
import json
import webbrowser
import pickle
from config import pickleDirectory

MESSAGE_CODES = {
    "PORT_ESTABLISHED_MESSAGE": "PORT_ESTABLISHED",
    "COMM_MANAGER_OPENED_MESSAGE": "COMM_MANAGER_OPENED",
    "REQUEST_BLOCKLIST_MESSAGE": "REQUEST_BLOCKLIST",
    "ENABLE_BLOCKLIST_MESSAGE": "ENABLE_BLOCKLIST",
    "ENABLE_BLOCKLIST_SUCCESSS_MESSAGE": "ENABLE_BLOCKLIST_SUCCESS"
}

lock_file = 'mainKlaus.lock'
log_file = 'mainKlaus.log'

TIMEOUT_TIME = 5
CHROME_PATH = "/Applications/Google Chrome.app"

# This is where the web browser block list is handled
def automate_browser(block_lists, settings):
    try:
        block_str = createWebsiteBlocklistFromBlocklists(block_lists)

        # Perform the task for these optional browsers
        # TODO remove i==1 with the users browsers from settings
        for i in range(1, 4):
            if i == 1 and settings.browsers[i - 1] == True:
                browser_exe = 'brave.exe'
                browser_name = 'Brave'
            elif i == 2 and settings.browsers[i - 1] == True:
                browser_exe = 'chrome.exe'
                browser_name = 'Google Chrome'
            elif i == 3 and settings.browsers[i - 1] == True:
                browser_exe = 'msedge.exe'
                browser_name = 'Microsoft\u200b Edge'
            else:
                continue

            if browser_name == 'Google Chrome': #use chrome extension
                try:

                    extension_id = 'goaaiijpbejcjepcjfindfjncboeolaj'

                    # The URL of the extension page in the Chrome Web Store
                    extension_url = f'chrome-extension://{extension_id}/options.html'

                    # Open the extension in the default browser
                    webbrowser.get('chrome').open_new(extension_url)

                    #T0D0: figure out how to send the ENABLE_BLOCKLIST_MESSAGE when the comm manager is
                    #successfully established. Maybe figure out how to send messages/talk between python files?

                except Exception as e:
                    print(f"Unable to send blocklist for Google Chrome: {e}")
                    continue
            else: #else use default method
                # Get screen DPI
                user32 = ctypes.windll.user32
                user32.SetProcessDPIAware()
                screen_width = user32.GetSystemMetrics(0)
                screen_height = user32.GetSystemMetrics(1)
                screen_dpi = user32.GetDpiForSystem()

                # Calculate zoom factor
                zoom_factor = screen_dpi / 96

                # Calculate click coordinates
                x = int(screen_width * 0.3 * zoom_factor)
                y = int(screen_height * 0.3 * zoom_factor)

                # Launch browser
                pyautogui.hotkey('win', 'r')
                pyautogui.typewrite(browser_exe)
                pyautogui.press('enter')

                # Wait for browser to open
                time.sleep(1)

                # Check if browser is maximized
                try:
                    win = pyautogui.getWindowsWithTitle(browser_name)[0]
                    is_maximized = win.isMaximized

                    # Maximize browser window if it's not already maximized
                    if not is_maximized:
                        pyautogui.hotkey('win', 'up')
                        # Wait for browser to maximize
                        time.sleep(.05)

                    # Navigate to extension URL
                    pyautogui.hotkey('ctrl', 'l')
                    pyautogui.typewrite('chrome-extension://akfbkbiialncppkngofjpglbbobjoeoe/options.html')
                    pyautogui.press('enter')

                    # Wait for extension to load
                    time.sleep(.7)

                    # Click the textbox
                    pyautogui.click(x, 2 * y)
                    time.sleep(.05)

                    # Select all text in textbox
                    pyautogui.hotkey('ctrl', 'a')

                    # Delete all text in textbox
                    pyautogui.press('backspace')

                    # Type in block list
                    pyautogui.typewrite(block_str.replace('BLOCKLIST:',''))

                    # Wait for text to be typed in
                    time.sleep(.1)

                    # Click the Save button
                    pyautogui.click(x / 1.3, 2.4 * y)
                    time.sleep(.05)

                    # Close the browser
                    pyautogui.hotkey('alt', 'f4')
                except IndexError:
                    print(f"Unable to find window for {browser_name}")
                    continue

    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"Web Blocking Automation Failed: {e}\n\n{tb}"
        print(error_message)

# Decrements the brightness by 1
def decrement_brightness():
    # Get the current brightness level
    completed = subprocess.run(
        ["powershell", "-Command", "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"],
        capture_output=True, text=True)
    current_brightness = int(completed.stdout.strip())

    # Decrement the brightness level by 1
    if current_brightness > 0:
        new_brightness = current_brightness - 1
        command = "(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1," + str(
            new_brightness) + ")"
        subprocess.run(["powershell", "-Command", command], capture_output=True)
        print(f"Brightness level set to {new_brightness}")
    else:
        print("Cannot decrement brightness level as it is already 0.")

def makePath(str1, str2):
    path = os.path.normpath(os.path.join(str1, str2))
    return path

def makeNormPath(str):
    return os.path.normpath(str)

def removeLockFile(): #removes the lock file
    os.remove(lock_file)
    writeToLogFile('Klaus lock file removed')

def writeToLogFile(message): #writes message to logfile
    with open(log_file, 'a') as f:
        f.write(f"{message}\n")

def ensureSingleton(): #makes sure that there is only one process running at a time using a lock file
    if isSingleton():
        writeLockFile()
        atexit.register(removeLockFile)
        print("This process is a singleton")
    else:
        print("Another instance is already running.")


def writeLockFile():
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))
        f.close()

def isSingleton(): #returns true if process is the only one, false if there's already another process
    if os.path.exists(lock_file):
        with open(lock_file, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            parent_process = psutil.Process(pid)
            if parent_process.name() == os.path.basename(__file__):
                return False
    return True

def handleExit():
    signal.signal(signal.SIGINT, exitSignalHandler)
    signal.signal(signal.SIGTERM, exitSignalHandler)

def exitSignalHandler(signal, frame):
    print(f"Klaus exiting with signal {signal}...")
    if os.path.exists(lock_file):
        removeLockFile()
    sys.exit(0)

def checkKlausRunning():
    if os.path.exists(lock_file):
        with open(lock_file, 'r') as f:
            pid = int(f.read().strip())
        if psutil.pid_exists(pid):
            return True
    return False

def runKlaus():
    # Run the parent script
    process = subprocess.Popen(['python3', 'Main.py', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the process to finish and get the output
    output, error = process.communicate()

    #Sends output and error
    sendMessage(output.decode('utf-8'))
    sendMessage(error.decode('utf-8'))

def openKlausInstance():
    if not checkKlausRunning():
        runKlaus()
        print("Running Klaus...")

def createWebsiteBlocklistFromBlocklists(block_lists):
    #Gathers website blocklist
    try:
        fullList = block_lists[1][0] + block_lists[1][1]
        block_str = '\n'.join(fullList) + '\n'
        block_list = f"BLOCKLIST:{block_str}"
        return(block_list)
    except Exception as e:
        print(f"Error occurred while creating website blocklist: {e}")

def createWebsiteBlocklistFromPickles():
  # Gathers website blocklist
  for filename in os.listdir(pickleDirectory):
    try:
      chosen_pickle = makePath(pickleDirectory, filename)

      with open(chosen_pickle, "rb") as file:
        data = pickle.load(file)

      if data["type"] == "WEBLIST":
        with open(chosen_pickle, "wb") as file:
          dataEntries = data["entries"]
          block_str = '\n'.join(dataEntries) + '\n'
          block_list = f'BLOCKLIST:{block_str}'
          pickle.dump(data, file)
          return block_list
    except Exception as e:
      print(f"Error occurred while creating website blocklist: {e}")

# Encode a message for transmission, given its content.
def encodeMessage(messageContent):
  # https://docs.python.org/3/library/json.html#basic-usage
  # To get the most compact JSON representation, you should specify (',', ':') to eliminate whitespace.
  # We want the most compact representation because the browser rejects # messages that exceed 1 MB.
  encodedContent = json.dumps(messageContent, separators=(',', ':')).encode('utf-8')
  encodedLength = struct.pack('@I', len(encodedContent))
  return {'length': encodedLength, 'content': encodedContent}

# Send an encoded message to stdout
def sendMessage(message):
  encodedMessage = encodeMessage(message)
  sys.stdout.buffer.write(encodedMessage['length'])
  sys.stdout.buffer.write(encodedMessage['content'])
  sys.stdout.buffer.flush()

def sendBlocklist():
  # if blocklist is not None and blocklist.startswith("BLOCKLIST:"):
  #     sendMessage(blocklist)
  # else:
  #     print("Couldn't send blocklist")
  sendMessage(createWebsiteBlocklistFromPickles())

