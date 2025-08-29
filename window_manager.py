import time
import mss
import win32gui
import win32process
import win32con
import win32api
import ctypes
import interception
from PIL import  Image
from utils import find_hwnds_by_process, get_ordered_pids, crop_image, estimate_color_range, find_fish_midpoint, \
     load_loot_table_templates, solve_captcha, is_captcha
from constants import *
import numpy as np
import random
import cv2
import configparser

class WindowManager:
    def __init__(self, process_name):
        self.window_index = {}
        self.num_clients = 0
        self.process_name = process_name
        self.update_window_list()
        self.loot_table_templates = load_loot_table_templates()
        config = configparser.ConfigParser()
        config.read(DEFAULT_CONFIG_PATH)
        self.loot_filter = config.get('DEFAULT', 'LOOT_FILTER').split(',')
        self.priority_filter = config.get('DEFAULT', 'PRIORITY_FILTER').split(',')
        interception.auto_capture_devices()


    def update_window_list(self):
        ordered_pids = get_ordered_pids(self.process_name)
        hwnds = find_hwnds_by_process(self.process_name)
        self.num_clients = len(ordered_pids)
        pid_hwnd_map = {win32process.GetWindowThreadProcessId(hwnd)[1]: hwnd for hwnd in hwnds}
        self.window_index = {i: pid_hwnd_map[pid] for i, pid in enumerate(ordered_pids) if pid in pid_hwnd_map}

    def activate_window_by_index(self, index):
        hwnd = self.window_index[index]
        active_hwnd = win32gui.GetForegroundWindow()
        if hwnd != active_hwnd:
            win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
            ctypes.windll.user32.BringWindowToTop(hwnd)
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SwitchToThisWindow(hwnd, True)
            win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.03)

        return hwnd

    def correct_windows_position(self):
        for window_id, hwnd in self.window_index.items():
            expected_x, expected_y = (GAME_WIDTH * window_id) - 8, -35
            rect = win32gui.GetWindowRect(hwnd)
            current_x, current_y = rect[0], rect[1]

            if (current_x, current_y) != (expected_x, expected_y):
                win32gui.MoveWindow(hwnd, expected_x, expected_y, GAME_WIDTH + 16, GAME_HEIGHT + 39, True)

    def solve_captcha(self):
        screenshot = self.capture_screenshot()
        temp = is_captcha(screenshot)
        if temp:
            x1, y1, = temp
        else:
            return False
        window_id = x1//GAME_WIDTH
        self.activate_window_by_index(window_id)
        # pierw klika refreshbutton zeby na pewno sprawdzać nową captche
        interception.move_to(x1 + CAPTCHA_REFRESH_XRELOFFSET, y1 + CAPTCHA_REFRESH_YRELOFFSET)
        time.sleep(0.1)
        interception.click(button="left")
        time.sleep(0.5)
        # robi screena nowej captchy
        screenshot = self.capture_screenshot()
        captcha_img = crop_image(screenshot, x1 + CAPTCHA_XRELOFFSET, y1 + CAPTCHA_YRELOFFSET, CAPTCHA_WIDTH,
                                 CAPTCHA_HEIGHT)
        im = Image.fromarray(captcha_img)
        im.save("captchas/captcha.jpeg")
        # wysyla screena hindusom
        captcha_result = solve_captcha("captchas/captcha.jpeg")
        if captcha_result: #jezeli zwróci false to po prostu w next próbie może sie uda z inna captcha (refresh)
            print("Rozwiązana CAPTCHA:", captcha_result)
            # klikanie inputa
            interception.move_to(x1 + CAPTCHA_INPUT_XRELOFFSET, y1 + CAPTCHA_INPUT_YRELOFFSET)
            time.sleep(0.1)
            interception.click(button="left")
            time.sleep(0.3)
            for char in captcha_result:
                interception.press(char)
                time.sleep(random.uniform(0.2,0.6)) # mimikowanie normalnego wpisywania
            time.sleep(0.3)
            # klikanie przycisku do wyslania captchy
            interception.move_to(x1 + CAPTCHA_BUTTON_XRELOFFSET, y1 + CAPTCHA_BUTTON_YRELOFFSET)
            time.sleep(0.1)
            interception.click(button="left")
            print(f"CAPTCHA ROZWIĄZANA Z KODEM: {captcha_result}")
            time.sleep(2)

    def close_technical_brake(self, technical_brake_loc):
        x1, y1 = technical_brake_loc
        interception.move_to(x1 + TECHNICAL_BRAKE_XRELOFFSET, y1 + TECHNICAL_BRAKE_YRELOFFSET)
        time.sleep(0.1)
        interception.click(button="left")
        time.sleep(0.1)

    def send_key(self, key, presses = 1):
        interception.press(key, presses= presses)

    def capture_screenshot(self):
        with mss.mss() as sct:
            monitor = {
                "top": OBS_YOFFSET,
                "left": 0,
                "width": GAME_WIDTH * self.num_clients,
                "height": GAME_HEIGHT
            }

            screenshot = sct.grab(monitor)

            img_np = np.array(Image.frombytes("RGB", screenshot.size, screenshot.rgb))

            return img_np

    def fishbot_minigame(self, screenshot, window_id):
        self.activate_window_by_index(window_id)
        x1, y1 = (GAME_WIDTH * window_id) + MINIGAME_XOFFSET, MINIGAME_YOFFSET
        screenshot_cropped = crop_image(screenshot, x1, y1, MINIGAME_WIDTH, MINIGAME_HEIGHT)
        screenshot_gray = cv2.cvtColor(screenshot_cropped, cv2.COLOR_BGR2GRAY)

        screenshot_sample = screenshot_gray[:, 0]
        color_range = estimate_color_range(screenshot_sample)

        if color_range:
            if color_range[0] >= 3:
                object_mid = find_fish_midpoint(screenshot_gray)
                if object_mid is not None:
                    color_mid = color_range[0] + int(
                        (abs(color_range[1] - color_range[0])) * random.uniform(*MINIGAME_SPACE_CLICK_THRESHOLD))
                    color_low = color_range[0] + int(
                        (abs(color_range[1] - color_range[0])) * random.uniform(*MINIGAME_DOUBLE_SPACE_CLICK_THRESHOLD))

                    if object_mid[1] > color_low:
                        print(f"{" " * window_id}MINIGAME {window_id + 1} TRIPLE SPACEBAR")
                        self.send_key("space", presses=3)
                    elif object_mid[1] > color_mid:
                        print(f"{" " * window_id}MINIGAME {window_id + 1} SPACEBAR")
                        self.send_key("space")
            else:
                return True
        return False
