import ctypes
import subprocess
import time
import traceback
import os
import sys
import portalocker
import queue

# set up logging
import logging

logging.basicConfig(filename="mainKlaus.log", encoding="utf-8", level=logging.DEBUG, format='%(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S')

try:
    import pyautogui
except ImportError:
    pass

try:
    import lib_programname
except ImportError:
    lib_programname = None

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
    "ENABLE_BLOCKLIST_SUCCESS_MESSAGE": "ENABLE_BLOCKLIST_SUCCESS",
    "GET_EXTENSION_ID_MESSAGE": "GET_ID",
    "OPEN_KLAUS_MESSAGE": "OPEN_KLAUS"
}

lock_file = 'mainKlaus.lock'
log_file = 'mainKlaus.log'

TIMEOUT_TIME = 5
CHROME_PATH = "/Applications/Google Chrome.app"

toCommManagerQueue = queue.Queue()
toNativeKlausQueue = queue.Queue()


def sendMessageToCommManager(msg):
    toCommManagerQueue.put(msg)


def readMessageFromCommManager():
    while not toNativeKlausQueue.empty():
        msg = toNativeKlausQueue.get_nowait()
        return msg


# This is where the web browser block list is handled
def automate_browser(block_lists, settings, blocker_on):
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

            if sys.platform == "win32":
                if blocker_on:
                    if browser_name == 'Google Chrome':  # use chrome extension
                        try:
                            automateChrome()
                        except Exception as e:
                            print(f"Unable to send blocklist for Google Chrome: {e}")
                            continue
                    else:  # else use default method
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
                            pyautogui.typewrite(block_str.replace('BLOCKLIST:', ''))

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
                else:
                    continue

    except Exception as e:
        tb = traceback.format_exc()
        error_message = f"Web Blocking Automation Failed: {e}\n\n{tb}"
        print(error_message)


def automateChrome():
    chromePath = makeNormPath('C:\Program Files\Google\Chrome\Application\chrome.exe')
    registerBrowser('chrome', chromePath)

    extension_id = getGlobalVar("EXTENSION_ID")

    # extension_id = 'dfjgcclcalfbaaenggppkhjklmdnbjce'

    # The URL of the extension page in the Chrome Web Store
    extension_url = f'chrome-extension://{extension_id}/options.html'

    openInBrowser(extension_url, 'chrome')

    # T0D0: figure out how to send the ENABLE_BLOCKLIST_MESSAGE when the comm manager is
    # successfully established. Maybe figure out how to send messages/talk between python files?


def registerBrowser(browserName, path):
    path = makeNormPath(path)  # just in case path hasn't been normalized
    if os.path.exists(path):
        try:
            webbrowser.register(browserName, None, webbrowser.BackgroundBrowser(path))
            # print("Careful! While the browser path exists it might not be correct")
        except webbrowser.Error as e:
            print("Error while registering browser: " + e)
    else:
        print("This browser path doesn't exist!")


def setGlobalVar(name, value):
    dataToAdd = {name: value}
    try:
        if os.stat("data.json").st_size == 0:
            with open('data.json', 'w') as f:
                json.dump(dataToAdd, f)
        else:
            with open("data.json", "r") as f:
                data = json.load(f)
            with open("data.json", "w") as f:
                data.update(dataToAdd)
                json.dump(data, f)
    except (EOFError, FileNotFoundError) as e:
        print("Error in setting global variable: " + e)


def getGlobalVar(key):
    with open('data.json', 'r') as f:
        data = json.load(f)
        if (key in data):
            return data[key]
        else:
            print("Item doesn't exist")


def openInBrowser(url, browserName):
    try:
        browser = webbrowser.get(browserName)
        browser.open(url)
        print(f"Opened {url} in {browserName}")
    except webbrowser.Error as e:
        print("Error while opening in browser: " + e)
    except Exception as e:
        print("Unable to open in browser " + e)


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


def runKlaus():
    # Run the parent script
    subprocess.Popen([sys.executable, 'Main.py', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def createWebsiteBlocklistFromBlocklists(block_lists):
    # Gathers website blocklist
    # try:
    fullList = block_lists[1][0] + block_lists[1][1]
    block_str = '\n'.join(fullList) + '\n'
    block_list = f"BLOCKLIST:{block_str}"
    setGlobalVar("website_blocklist", block_list)
    return (block_list)
    # except Exception as e:
    #     print(f"Error occurred while creating website blocklist: {e}")


# Gathers website blocklist
def createWebsiteBlocklistFromPickles():
    block_list = []
    block_list_str = ""

    for filename in os.listdir(pickleDirectory):
        try:
            chosen_pickle = makePath(pickleDirectory, filename)

            with open(chosen_pickle, "rb") as file:
                portalocker.lock(file, portalocker.LOCK_EX)
                data = pickle.load(file)

                if data["type"] == "WEBLIST":
                    dataEntries = data["entries"]

                    block_list.append(dataEntries)

                portalocker.unlock(file)

        except Exception as e:
            print(f"Error occurred while creating website blocklist from pickles: {e}")
            return e  # T0D0: HANDLE EXCEPTIONS BETTER

    block_list_str = block_list_str.join(str(x) for x in block_list)

    decoded_string = bytes(block_list_str, "utf-8").decode("unicode_escape")
    decoded_string = decoded_string.replace("']['", "\n")
    decoded_string = decoded_string.replace("['", "")
    decoded_string = decoded_string.replace("']", "")
    decoded_string = ",".join(decoded_string.split('\n'))

    return decoded_string


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

    block_list = createWebsiteBlocklistFromPickles()

    if block_list == "":
        sendMessage("EMPTY_BLOCKLIST")
    else:
        tagged_block_list_str = f'BLOCKLIST:{block_list}'

        sendMessage(tagged_block_list_str)
