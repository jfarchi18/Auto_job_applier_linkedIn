'''
Author:     Sai Vignesh Golla
LinkedIn:   https://www.linkedin.com/in/saivigneshgolla/

Copyright (C) 2024 Sai Vignesh Golla

License:    GNU Affero General Public License
            https://www.gnu.org/licenses/agpl-3.0.en.html

GitHub:     https://github.com/GodsScion/Auto_job_applier_linkedIn

Support me: https://github.com/sponsors/GodsScion

version:    26.01.20.5.08
'''

import os
import subprocess
import time
from modules.helpers import get_default_temp_profile, make_directories
from config.settings import run_in_background, stealth_mode, disable_extensions, safe_mode, file_name, failed_file_name, logs_folder_path, generated_resume_path
from config.questions import default_resume_path
if stealth_mode:
    import undetected_chromedriver as uc
else:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from modules.helpers import find_default_profile_directory, critical_error_log, print_lg
from selenium.common.exceptions import SessionNotCreatedException


def kill_all_chrome():
    """Kill all Chrome and chromedriver processes and wait until they're gone."""
    subprocess.run(["taskkill", "/f", "/t", "/im", "chrome.exe"], capture_output=True)
    subprocess.run(["taskkill", "/f", "/t", "/im", "chromedriver.exe"], capture_output=True)
    # Wait until chrome.exe is actually gone
    for _ in range(10):
        result = subprocess.run(["tasklist", "/fi", "imagename eq chrome.exe"], capture_output=True, text=True)
        if "chrome.exe" not in result.stdout:
            break
        time.sleep(1)
    time.sleep(2)


def clean_profile_locks(profile_dir):
    """Remove lock files that prevent Selenium from using the profile."""
    for lock_name in ["SingletonLock", "SingletonSocket", "SingletonCookie"]:
        lock_path = os.path.join(profile_dir, lock_name)
        if os.path.exists(lock_path):
            try: os.remove(lock_path)
            except: pass


def createChromeSession():
    make_directories([file_name,failed_file_name,logs_folder_path+"/screenshots",default_resume_path,generated_resume_path+"/temp"])
    options = uc.ChromeOptions() if stealth_mode else Options()
    if run_in_background:   options.add_argument("--headless")
    if disable_extensions:  options.add_argument("--disable-extensions")

    profile_dir = find_default_profile_directory()

    if profile_dir and not safe_mode:
        print_lg("Closing Chrome to use your real profile...")
        kill_all_chrome()
        clean_profile_locks(profile_dir)
        options.add_argument(f"--user-data-dir={profile_dir}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--disable-session-crashed-bubble")
        print_lg(f"Using your Chrome profile: {profile_dir}")
    else:
        print_lg("Using guest profile.")
        options.add_argument(f"--user-data-dir={get_default_temp_profile()}")

    if stealth_mode:
        print_lg("Downloading Chrome Driver...")
        driver = uc.Chrome(options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.maximize_window()
    wait = WebDriverWait(driver, 5)
    actions = ActionChains(driver)
    return options, driver, actions, wait


try:
    options, driver, actions, wait = None, None, None, None
    options, driver, actions, wait = createChromeSession()
except Exception as e:
    # DON'T silently retry with guest - show the actual error
    print_lg(f"ERROR creating Chrome session: {e}")
    critical_error_log("In Opening Chrome", e)
    from pyautogui import alert
    alert(f"Chrome failed to start: {e}\n\nMake sure Chrome is fully closed first.", "Error")
    try: driver.quit()
    except: exit()
