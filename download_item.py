import json
import os
import time

import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def login_to_site(driver, username, password):
    wait = WebDriverWait(driver, 30)
    login_input = wait.until(EC.element_to_be_clickable((By.ID, 'elogin')))
    login_input.clear()
    login_input.send_keys(username)

    password_input = wait.until(EC.element_to_be_clickable((By.ID, 'epassword')))
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(13)
    submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'form_button_submit')))
    submit_button.click()


def click_element(driver, by_type, identifier, waittime=30):
    wait = WebDriverWait(driver, waittime)
    while True:
        try:
            link = wait.until(EC.element_to_be_clickable((by_type, identifier)))
            link.click()
            return  # Successfully clicked, exit function
        except selenium.common.exceptions.ElementClickInterceptedException:
            # If click failed, wait a bit and try again
            driver.implicitly_wait(5)


def setup_driver_and_login(username, password):
    if os.name == 'posix':
        gecko_path = './geckodriver'
    else:
        gecko_path = './geckodriver.exe' 
    service = Service(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service)
    wait = WebDriverWait(driver, 120)
    driver.get('https://www.epicov.org/epi3/frontend')
    login_to_site(driver, username, password)

    return driver


def download_file(id_list):
    js_list = json.dumps(id_list)
    js_code = f"""
    var isList = {js_list};

    var command_tail = {{
        'wid': sys.WID,
        'pid': sys.PID,
        'cid': sys.CID,
        'params': {{
            'col': 'q'
        }},
        'equiv': null
    }};

    isList.forEach((num) => {{
        sys.command_queue.push({{
            'wid': sys.WID,
            'pid': sys.PID,
            'cid': sys.CID,
            'cmd': 'ChangeValue',
            'params': {{
                'row_id': num,
                'col_name': 'c',
                'value': true
            }},
            'equiv': null
        }});
    }})
    """
    return js_code


def perform_actions(driver):
    click_element(driver, By.LINK_TEXT, "EpiFlu™")
    click_element(driver, By.XPATH, "//div[text()='Search & Browse']")
    click_element(driver, By.XPATH, "//button[text()='Search']")


username = ''
password = ''
proxies = {}
page_json = 'GisAid_id.json'

with open(page_json, 'r') as file:
    data = json.load(file)

n = 0
while True:
    driver = setup_driver_and_login(username, password)
    time.sleep(15)
    perform_actions(driver)
    sid, wid, pid = driver.execute_script("return [sys.SID, sys.WID, sys.PID];")
    cid = driver.execute_script("return sys.command_queue;")[0]['cid']
    driver.execute_script(f"sys.CID='{cid}';")

    print(f"sid:{sid}, wid:{wid}, pid:{pid}, cid:{cid}")
    i = 8000 * n
    cid = driver.execute_script("return sys.command_queue;")[0]['cid']
    driver.execute_script(f"sys.CID='{cid}';")
    selected_elements = data[i:i + 8000]
    driver.execute_script(download_file(selected_elements))
    n = n + 1
    input(f"{i} Datas have been download, Press any key to continue... \n")
    driver.close()
