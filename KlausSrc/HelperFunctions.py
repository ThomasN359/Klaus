import ctypes
import subprocess
import time
import traceback

import pyautogui

from CommunicationManager import sendBlocklist

# This is where the web browser block list is handled
def automate_browser(block_lists, settings):
    try:
        # create the mega block list by combining all the current lists
        fullList = block_lists[1][0] + block_lists[1][1]
        block_str = '\n'.join(fullList) + '\n'

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
                    sendBlocklist(block_str)
                except:
                    print(f"Unable to send blocklist for Google Chrome")
                    continue
            else: #else use default method
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
                    pyautogui.typewrite(block_str)

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