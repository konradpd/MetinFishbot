# Bot Installation and Configuration Guide

This document provides step-by-step instructions for installing and configuring the bot.

## 1. Interception Driver
- Download: [Interception v1.0.1](https://github.com/oblitum/Interception/releases/download/v1.0.1/Interception.zip)  
- Extract the archive.  
- Open the extracted folder.  
- Navigate to the **command line installer** directory.  
- Copy the folder path.  
- Open **Command Prompt** as administrator.  
- Run the following command (replace with your copied path):  
  ```cmd
  cd /d "your_path_here"
  install-interception.exe /install
  ```  
- Restart your computer.

## 2. Python 3.12.2
- Download: [Python 3.12.2 (Windows 64-bit)](https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe)  
- Run the installer (administrator rights may be required, except on Windows 11).  
- Enable **Add to PATH** and **Use Administrator Privileges** (if available).  
- Complete the installation.

## 3. Pip
- Open Command Prompt and check if pip is installed:  
  ```cmd
  pip
  ```
- If not, update or install pip:  
  ```cmd
  py -m pip install --upgrade pip
  ```
- Verify installation again with `pip`. If it still fails, troubleshoot manually.

## 4. OBS
- Run OBS as administrator.

## 5. Requirements.txt
- Download the bot.  
- In the bot folder, open Command Prompt (type `cmd` in the path bar).  
- Install dependencies:  
  ```cmd
  pip install -r requirements.txt
  ```

## 6. Configuration File (config.ini)
The configuration file allows you to customize the bot’s behavior. Do not remove any keys; only edit values.

- `bait_keys` – list of keys to be used for bait (example: `1,2,3,4,5`).  
- `effect_keys` – keys used for activating effects (example: `4`).  
- `upgrade_fishingrod_notification` – set to `True` to enable notifications when fishing rods can be upgraded.  
- `automatic_captcha` – set to `True` to enable automatic captcha solving.  
- `logs` – set to `True` to enable logging.  
- `stop_key_combination` – key or combination that stops the bot (example: `p` or `shift+p`).  
- `brake_chance` – probability for triggering a break (example: `0.00002`).  
- `break_duration` – break duration range in seconds, separated by a comma (example: `300,900`).  
- `loot_filter` – list of items to skip, separated by commas. Replace spaces with underscores. Example:
  ```ini
  loot_filter = wybielacz,farba_do_wlosow,pierscien_jezyka
  ```
- `priority_filter` – list of valuable items that the bot should prioritize. Example:
  ``` ini
  priority_filter = fasolka_zen,zloty_karas,zwoj_blogoslawienstwa,zwoj_boga_smokow,zwoj_egzorcyzmu,rada_pustelnika,ekstraktor_skaz,magiczny_metal,kamien_kowala)
  ```

## 7. Sound Alerts
- Go to the **templates** folder.  
- Preview available alerts:  
  - `captcha_alert.wav`  
  - `exp_alert.wav`  
- You may replace these files with your own, but keep the same names and `.wav` format.

## 8. Metin Settings (Important)
- Window size: **640x540**  
- Font: **Arial**  
- Disable chat and lock all except whispers.

## 9. Running the Bot
- Start the bot with one client only, using `run` as administrator.  
- Enter the number of clients.  
- Open the remaining clients.  
- Arrange OBS and console so they do not interfere.  
- Enter the current fishing rod EXP and required EXP for upgrade.  
  - If you do not want notifications, simply press Enter without input.
