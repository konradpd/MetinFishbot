import psutil
import cv2
import numpy as np
import time
import win32gui
import win32process
import sys
from constants import *
import keyboard
from twocaptcha import TwoCaptcha
import configparser
import sounddevice as sd
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="pydub.utils")
from pydub import AudioSegment
import os
from dotenv import load_dotenv

load_dotenv()

# Read templates
MINIGAME_TEMPLATE = cv2.imread(MINIGAME_TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
MINIGAME_FISH_TEMPLATE = cv2.imread(MINIGAME_FISH_TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
CHAT_MSG_TEMPLATE_1 = cv2.imread(CHAT_MSG_TEMPLATE_PATH_1, cv2.IMREAD_UNCHANGED)
CHAT_MSG_TEMPLATE_2 = cv2.imread(CHAT_MSG_TEMPLATE_PATH_2, cv2.IMREAD_UNCHANGED)
CAPTCHA_HEADER_TEMPLATE = cv2.imread(CHAPTCHA_HEADER_TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
RECIEVED_TEMPLATE = cv2.imread(RECIEVED_TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
LOST_TEMPLATE = cv2.imread(LOST_TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
UPGRADE_FISHINGROD_TEMPLATE = cv2.imread(UPGRADE_FISHINGROD_TEMPLATE_PATH, cv2.IMREAD_UNCHANGED)
TECHNICAL_BRAKE_TEMPLATE = cv2.imread(TECHNICAL_BRAKE_PATH, cv2.IMREAD_UNCHANGED)
if (MINIGAME_FISH_TEMPLATE is None
        or CHAT_MSG_TEMPLATE_1 is None
        or CHAT_MSG_TEMPLATE_2 is None
        or CAPTCHA_HEADER_TEMPLATE is None
        or RECIEVED_TEMPLATE is None
        or LOST_TEMPLATE is None
        or UPGRADE_FISHINGROD_TEMPLATE is None
        or TECHNICAL_BRAKE_TEMPLATE is None
        or MINIGAME_TEMPLATE is None):
    print("Error: Object template not found!")
    exit()
MINIGAME_TEMPLATE_GRAY =  cv2.cvtColor(MINIGAME_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)
MINIGAME_FISH_TEMPLATE_GRAY =  cv2.cvtColor(MINIGAME_FISH_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)
CHAT_MSG_TEMPLATE_1_GRAY  = cv2.cvtColor(CHAT_MSG_TEMPLATE_1[:, :, :3], cv2.COLOR_BGR2GRAY)
CHAT_MSG_TEMPLATE_2_GRAY  = cv2.cvtColor(CHAT_MSG_TEMPLATE_2[:, :, :3], cv2.COLOR_BGR2GRAY)
CAPTCHA_HEADER_TEMPLATE_GRAY  = cv2.cvtColor(CAPTCHA_HEADER_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)
RECIEVED_TEMPLATE_GRAY = cv2.cvtColor(RECIEVED_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)
LOST_TEMPLATE_GRAY = cv2.cvtColor(LOST_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)
UPGRADE_FISHINGROD_TEMPLATE_GRAY = cv2.cvtColor(UPGRADE_FISHINGROD_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)
TECHNICAL_BRAKE_TEMPLATE_GRAY =cv2.cvtColor(TECHNICAL_BRAKE_TEMPLATE[:, :, :3], cv2.COLOR_BGR2GRAY)


config = configparser.ConfigParser()
config.read(DEFAULT_CONFIG_PATH)

STOP_KEY_COMBINATION = config.get('DEFAULT', 'STOP_KEY_COMBINATION')


def menu(client_states, window_manager):
    while True:
        option = input(f"Zatrzymano skrótem: '{STOP_KEY_COMBINATION}'\n"
                       " 1.Powrót do łowienia\n"
                       " 2.Wyjście\n")
        try:
            option = int(option)
        except:
            option = 0

        if option == 1:
            for i in range(window_manager.num_clients):
                client_states[i]["state"] = STATE_OFF
            break
        elif option == 2:
            exit()
        else:
            print("Wpisz cyfre 1 lub 2")


def get_ordered_pids(process_name):
    file_pids = load_pids_from_file()
    current_pids = find_pids_by_process(process_name)
    if file_pids:
        are_all_file_pids_in_current_pids = True
    else:
        are_all_file_pids_in_current_pids = False
    for pid in file_pids:
        if pid not in current_pids:
            are_all_file_pids_in_current_pids = False

    if are_all_file_pids_in_current_pids:
        return file_pids

    num_clients = int(input("Podaj liczbę okien do otwarcia: "))

    print(f"Otwieraj po kolei okna {process_name}...")

    ordered_pids = []
    while len(ordered_pids) < num_clients:
        current_pids = find_pids_by_process(process_name)

        new_pids = [pid for pid in current_pids if pid not in ordered_pids]
        if new_pids:
            ordered_pids.extend(new_pids)
            for pid in new_pids:
                print(f"Dodano nowe okno: PID={pid}")
        time.sleep(0.1)
    save_pids_to_file(ordered_pids)
    return ordered_pids

def save_pids_to_file(pids, filename="pids.txt"):
    with open(filename, "w") as file:
        for pid in pids:
            file.write(f"{pid}\n")

def load_pids_from_file(filename="pids.txt"):
    try:
        with open(filename, "r") as file:
            return [int(line.strip()) for line in file]
    except FileNotFoundError:
        print("PID file not found. Generating a new list...")
        return []
    except ValueError:
        print("Error reading PID file. Ensure data format is correct.")
        return []

def find_pids_by_process(process_name):
    random_set = set()
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name:
            random_set.add(proc.info['pid'])

    pids_found = set()

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in random_set:
                pids_found.add(pid)

    win32gui.EnumWindows(enum_callback, None)
    return list(pids_found)

def find_hwnds_by_process(process_name):
    pids = {proc.info['pid'] for proc in psutil.process_iter(['pid', 'name']) if proc.info['name'].lower() == process_name}
    windows = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            if pid in pids:
                windows.append(hwnd)

    win32gui.EnumWindows(enum_callback, None)
    return windows

def crop_image(image, x, y, width, height):
    return image[y:y+height, x:x+width]


def is_minigame(screenshot, window_id):
    x1, y1 = (GAME_WIDTH * window_id) + MINIGAME_CHECK_XOFFSET, MINIGAME_CHECK_YOFFSET
    screenshot_cropped = crop_image(screenshot, x1, y1, MINIGAME_CHECK_WIDTH, MINIGAME_CHECK_HEIGHT)
    screenshot_gray = cv2.cvtColor(screenshot_cropped, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(screenshot_gray, MINIGAME_TEMPLATE_GRAY, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    return max_val >= 0.9


def is_chat_message(screenshot, window_id, templates=[CHAT_MSG_TEMPLATE_1_GRAY, CHAT_MSG_TEMPLATE_2_GRAY], xoffset = 0, yoffset = 0):
    x1, y1 = (GAME_WIDTH * window_id) + CHAT_MSG_XOFFSET + xoffset, CHAT_MSG_YOFFSET + yoffset
    screenshot_cropped = crop_image(screenshot, x1, y1, CHAT_MSG_WIDTH, CHAT_MSG_HEIGHT)
    screenshot_gray = cv2.cvtColor(screenshot_cropped, cv2.COLOR_BGR2GRAY)


    for template in templates:
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val >= CHAT_MSG_THRESHOLD:
            return True
    return False

def is_captcha(screenshot):
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, CAPTCHA_HEADER_TEMPLATE_GRAY, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= CAPTCHA_HEADER_THRESHOLD:
        return max_loc
    return None

def is_technical_brake(screenshot):
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(screenshot_gray, TECHNICAL_BRAKE_TEMPLATE_GRAY, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val >= CAPTCHA_HEADER_THRESHOLD:
        return max_loc
    return None



def play_sound(alert_path):
    audio = AudioSegment.from_file(alert_path)
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    samples /= np.iinfo(audio.array_type).max
    fs = audio.frame_rate

    print(f"WCIŚNIJ '{STOP_KEY_COMBINATION}' BY ZATRZYMAĆ ALARM!")

    while not keyboard.is_pressed(STOP_KEY_COMBINATION):
        sd.play(samples, samplerate=fs)

        while sd.get_stream().active:
            if keyboard.is_pressed(STOP_KEY_COMBINATION):
                sd.stop()
                return
        time.sleep(2)

def estimate_color_range(pixel_values, t_min=45, max_gap=3):
    pixel_values = np.array(pixel_values)

    mask = pixel_values >= t_min

    true_indices = np.where(mask)[0]
    if len(true_indices) == 0:
        return None

    clusters = []

    current_cluster_start = true_indices[0]
    current_cluster_end = true_indices[0]

    for idx in true_indices[1:]:
        if idx - current_cluster_end <= max_gap + 1:
            current_cluster_end = idx
        else:
            clusters.append((current_cluster_start, current_cluster_end))
            current_cluster_start = idx
            current_cluster_end = idx

    clusters.append((current_cluster_start, current_cluster_end))

    best_cluster = max(clusters, key=lambda cl: cl[1] - cl[0])
    return best_cluster

def find_fish_midpoint(screenshot_gray):
    result = cv2.matchTemplate(screenshot_gray, MINIGAME_FISH_TEMPLATE_GRAY, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    if max_val > FISH_ICON_THRESHOLD:
        return (max_loc[0] + 8, max_loc[1] + 8)
    return None

def load_loot_table_templates():
    loot_table_images = {}
    for filename in os.listdir(LOOT_TABLE_PATH):
        file_path = os.path.join(LOOT_TABLE_PATH, filename)

        if os.path.isfile(file_path) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
            img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                img_gray = cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2GRAY)

                loot_name = os.path.splitext(filename)[0]
                loot_table_images[loot_name] = img_gray

    # Sortowanie od najdłuższego do najkrótszego, żeby np. Duży Karaś nie został zczytany jako Karaś
    loot_table_images_sorted = sorted(loot_table_images.items(), key=lambda item: len(item[0]), reverse=True)
    return loot_table_images_sorted



def filter_loot(screenshot, window_id, loot_table_templates):
    for key, template in loot_table_templates:
        if is_chat_message(screenshot, window_id, templates=[template]):
            return key
    return None


def smooth_move(interception, x1, y1, x2, y2, duration=1, steps=40):
    dx = np.linspace(x1, x2, steps)
    dy = np.linspace(y1, y2, steps)
    interval = duration / steps  # czas między krokami
    interception.mouse_up("left")
    interception.mouse_down(button="left")
    time.sleep(0.05)
    for x, y in zip(dx, dy):
        interception.mouse_down(button="left")
        with interception.hold_mouse("left"):
            interception.move_to(int(x), int(y))
        interception.mouse_down("left")
        time.sleep(interval)
    interception.mouse_up("left")

def request(image_path):
    api_key = os.getenv('APIKEY_2CAPTCHA')
    solver = TwoCaptcha(api_key)
    
    try:
        result = solver.normal(image_path)  # output {'captchaId': '...', 'code': '...'}
        return result
    except Exception as e:
        return {'error': str(e)}

def solve_captcha(image_path):
    while True:
        captcha_result = request(image_path)
        if 'error' in captcha_result:
            print(f"Błąd podczas rozwiązywania captchy: {captcha_result['error']}")
        elif 'code' in captcha_result:
            return str(captcha_result['code'])
        else:
            print("Nieoczekiwany format odpowiedzi:", captcha_result)



