import time
import random
import keyboard
import gc
import configparser
from utils import is_minigame, is_chat_message, is_captcha, play_sound, is_technical_brake, \
    UPGRADE_FISHINGROD_TEMPLATE_GRAY, menu, filter_loot
from window_manager import WindowManager
from constants import *

# Load configuration
config = configparser.ConfigParser()
config.read(DEFAULT_CONFIG_PATH)

BAIT_KEYS = config.get('DEFAULT', 'BAIT_KEYS').split(',')
EFFECT_KEYS = config.get('DEFAULT', 'EFFECT_KEYS').split(',')
LOGS = config.getboolean('DEFAULT', 'LOGS')
UPGRADE_FISHINGROD_NOTIFICATION = config.getboolean('DEFAULT', 'UPGRADE_FISHINGROD_NOTIFICATION')
AUTOMATIC_CAPTCHA = config.getboolean('DEFAULT', 'AUTOMATIC_CAPTCHA')
STOP_KEY_COMBINATION = config.get('DEFAULT', 'STOP_KEY_COMBINATION')
BREAK_CHANCE = config.getfloat('DEFAULT', 'BRAKE_CHANCE')
BREAK_DURATION = [int(x) for x in config.get('DEFAULT', 'BREAK_DURATION').split(',')]

def main_loop(window_manager):
    client_states = [{'state': STATE_OFF, 'state_entry_time': time.time(), 'loot':None} for _ in range(window_manager.num_clients)]

    while True:
        gc.collect()
        # MENU
        if keyboard.is_pressed(STOP_KEY_COMBINATION):
            menu(client_states, window_manager)

        if random.random() < BREAK_CHANCE:
            break_duration = random.randint(*BREAK_DURATION)
            print(f"RANDOM BREAK FOR {break_duration/60} MINUTES")
            time.sleep(break_duration)
            print("COMING BACK TO FISHING AFTER THE BREAK")
        screenshot = window_manager.capture_screenshot()
        captcha_loc = is_captcha(screenshot)
        if captcha_loc is not None:
            if AUTOMATIC_CAPTCHA:
                window_manager.solve_captcha()
            else:
                play_sound(CAPTCHA_ALERT_PATH)
                menu(client_states, window_manager)
            for window_id in range(window_manager.num_clients):
                client_state = client_states[window_id]
                client_state['state'] = STATE_OFF
                client_state['state_entry_time'] = time.time()+10
            continue

        technical_brake_loc = is_technical_brake(screenshot)
        if technical_brake_loc is not None:
            window_manager.close_technical_brake(technical_brake_loc)
        for window_id in range(window_manager.num_clients):
            client_state = client_states[window_id]
            current_time = time.time()
            # if client_state['state'] == STATE_PRIORITY_MINIGAME:
            #     screenshot = window_manager.capture_screenshot()
            #     minigame_check = is_minigame(screenshot, window_id)
            #     if minigame_check:
            #         result = window_manager.fishbot_minigame(screenshot, window_id)
            #
            #     if result or not minigame_check:
            #         client_state['state'] = STATE_OFF
            #         client_state['state_entry_time'] = time.time() + 1.5
            #         print(f"MINIGAME END {window_id + 1}")


            if client_state['state'] == STATE_BURNING_MINIGAME:
                screenshot = window_manager.capture_screenshot()
                minigame_check = is_minigame(screenshot, window_id)
                if minigame_check:
                    result = window_manager.fishbot_minigame(screenshot, window_id)

                if random.random() < 0.1:
                    print(f"BURINING MINIGAME {window_id + 1} RIGHT NOW!")
                    result = True

                if result or not minigame_check:
                    client_state['state'] = STATE_OFF
                    client_state['state_entry_time'] = time.time() + 3
                    client_state['loot'] = None
                    print(f"MINIGAME END {window_id + 1}")
            elif client_state['state'] == STATE_MINIGAME:
                screenshot = window_manager.capture_screenshot()
                minigame_check = is_minigame(screenshot, window_id)
                if minigame_check:
                    result = window_manager.fishbot_minigame(screenshot, window_id)

                if result or not minigame_check:
                    client_state['state'] = STATE_OFF
                    client_state['state_entry_time'] = time.time() + 1.5
                    client_state['loot'] = None
                    print(f"MINIGAME END {window_id + 1}")

            elif client_state['state'] == STATE_WAITING_FOR_MINIGAME and current_time - client_state['state_entry_time'] > 0:
                if client_state['loot'] in window_manager.priority_filter:
                    print(f"MINIGAME START {window_id + 1} - PRIORYTET {loot}")
                    for cs in client_states:
                        if cs['loot'] not in window_manager.priority_filter:
                            cs['state'] = STATE_OFF
                            cs['state_entry_time'] = time.time()
                            cs['loot'] = None
                    client_states[window_id]['state'] = STATE_MINIGAME
                    client_states[window_id]['state_entry_time'] = time.time()
                elif not any(client['state'] == STATE_MINIGAME for client in client_states):
                    print(f"MINIGAME START {window_id + 1}")
                    if random.random() < 0.05:
                        print(f"RANDOMLY BURNING MINIGAME {window_id + 1} - 5% CHANCE")
                        client_state['state'] = STATE_BURNING_MINIGAME
                    else:
                        client_state['state'] = STATE_MINIGAME
                    client_state['state_entry_time'] = time.time()
                # else:
                #     client_state['state'] = STATE_OFF
                #     client_state['state_entry_time'] = time.time() + 5
                #     client_state['loot'] = None

            elif client_state['state'] == STATE_WAITING_TO_RETRIEVE_FISH and current_time - client_state['state_entry_time'] > 0:
                print(f"FISH RETRIEVED {window_id+1}")
                szansa = random.random()
                if szansa < 0.05:
                    print("RANDOMLY NOT CLICKING SPACE - 5% CHANCE")
                    client_state['state'] = STATE_OFF
                    client_state['state_entry_time'] = time.time() + 3
                elif szansa < 0.1:
                    print("RANDOMLY CLICKING SPACE TOO LATE - 5% CHANCE")
                    time.sleep(0.5)
                window_manager.activate_window_by_index(window_id)
                window_manager.send_key("space")
                time.sleep(0.2)
                screenshot = window_manager.capture_screenshot()
                if is_minigame(screenshot, window_id):
                    loot = filter_loot(screenshot, window_id, window_manager.loot_table_templates)
                    client_state['loot'] = loot
                    if loot in window_manager.loot_filter:
                        print(f"SPALAM {loot}")
                        client_state['state'] = STATE_OFF
                        client_state['state_entry_time'] = time.time() + 10
                    else:
                        print(f"MINIGAME FOUND {window_id+1}")
                        client_state['state'] = STATE_WAITING_FOR_MINIGAME
                        client_state['state_entry_time'] = time.time() + MINIGAME_WAIT_TIME
                else:
                    client_state['state'] = STATE_OFF
                    client_state['state_entry_time'] = time.time()

            elif client_state['state'] == STATE_WAITING_FOR_TEXT:
                if time.time() - client_state['state_entry_time'] > WAITING_FOR_TEXT_TIMEOUT:
                    print(f"TIMEOUT {window_id + 1}")
                    client_state['state'] = STATE_OFF
                    client_state['state_entry_time'] = time.time()
                    if LOGS:
                        print(f"Client {window_id + 1} timed out, switching state to {client_state['state']}.")
                elif is_chat_message(screenshot, window_id):
                    client_state['state'] = STATE_WAITING_TO_RETRIEVE_FISH
                    client_state['state_entry_time'] = time.time() + random.uniform(*FISH_RETRIEVAL_WAIT_TIME)

            elif client_state['state'] == STATE_OFF and current_time - client_state['state_entry_time'] > random.uniform(*STATE_RETRY_INTERVAL) and not any(client['state'] == STATE_MINIGAME for client in client_states):
                print(f"THROWING BAIT {window_id+1}")
                if UPGRADE_FISHINGROD_NOTIFICATION:
                    if is_chat_message(screenshot, window_id, templates=[UPGRADE_FISHINGROD_TEMPLATE_GRAY]) \
                        or is_chat_message(screenshot, window_id, templates=[UPGRADE_FISHINGROD_TEMPLATE_GRAY], yoffset=SECOND_MESSAGE_YOFFSET):
                        window_manager.activate_window_by_index(window_id)
                        window_manager.send_key('1')
                        window_manager.send_key('1')
                        print(f"ULEPSZ WĘDKĘ CLIENT {window_id+1}")
                        play_sound(UPGRADE_ALERT_PATH)
                        menu(client_states, window_manager)

                window_manager.activate_window_by_index(window_id)
                time.sleep(0.1)
                window_manager.send_key(random.choice(BAIT_KEYS))
                time.sleep(random.uniform(0.2,0.8))
                window_manager.send_key("space")
                client_state['state'] = STATE_WAITING_FOR_TEXT
                client_state['state_entry_time'] = time.time()

        time.sleep(MAIN_LOOP_SLEEP)
        gc.collect()

if __name__ == '__main__':
    window_manager = WindowManager("mt2009.exe")
    time.sleep(0.2)
    window_manager.correct_windows_position()
    input("Jeżeli masz wyszstko przygotowane - obs, cmd w miejscu które nie będzie przeszkadzać. Wciśnij ENTER")
    # window_manager.set_chat()
    main_loop(window_manager)
