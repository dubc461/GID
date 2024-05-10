#!/usr/bin/env python
# coding: utf-8
import json
import os
import re
import time
import tqdm

import requests
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def clean_html_tags(text):
    # Clean <strong> tags
    strong_pattern = re.compile(r'<strong[^>]*>(.*?)</strong>', re.IGNORECASE)
    text = strong_pattern.sub(r'\1', text)
    # Clean <span> tags and extract content and title
    span_pattern = re.compile(r'<span[^>]*title="([^"]*)"[^>]*>(.*?)</span>', re.IGNORECASE)
    span_pattern_notitle = re.compile(r"<[^>]+>")
    matches = span_pattern.findall(text)
    if matches:
        title, content = matches[-1]
        return f"{content} | {title}" if title else content
    if text == "---":
        return ''
    return span_pattern_notitle.sub("", text)


def clean_response(text):
    cleaned_data = {key: clean_html_tags(value) if isinstance(value, str) else value for key, value in text.items()}
    cleaned_data.pop('d')
    return cleaned_data


def read_continue_index():
    file_path = 'continue.txt'
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return int(content)
    else:
        return 0


def save_continue_index(index):
    file_path = 'continue.txt'
    with open(file_path, 'w') as file:
        file.write(str(index))


def login_to_site(driver, username, password):
    wait = WebDriverWait(driver, 30)
    login_input = wait.until(EC.element_to_be_clickable((By.ID, 'elogin')))
    login_input.clear()
    login_input.send_keys(username)
    password_input = wait.until(EC.element_to_be_clickable((By.ID, 'epassword')))
    password_input.clear()
    password_input.send_keys(password)
    time.sleep(15)
    submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'form_button_submit')))
    submit_button.click()


def click_element(driver, by_type, identifier, waittime=30):
    wait = WebDriverWait(driver, waittime)
    while True:
        try:
            link = wait.until(EC.element_to_be_clickable((by_type, identifier)))
            link.click()
            return
        except selenium.common.exceptions.ElementClickInterceptedException:
            driver.implicitly_wait(5)


def setup_driver_and_login(username, password):
    if os.name == 'posix':
        gecko_path = './geckodriver'
    else:
        gecko_path = './geckodriver.exe'

    service = Service(executable_path=gecko_path)
    driver = webdriver.Firefox(service=service)
    wait = WebDriverWait(driver, 120)
    driver.get('https://www.epicov.org/epi3/frontend#48bd6b')
    login_to_site(driver, username, password)
    return driver


def perform_actions(driver):
    click_element(driver, By.LINK_TEXT, "EpiFlu™")
    click_element(driver, By.XPATH, "//div[text()='Search & Browse']")
    click_element(driver, By.XPATH, "//button[text()='Search']")


username = ''
password = ''
page_number = 19100
proxies = {}

driver = setup_driver_and_login(username, password)
time.sleep(15)
perform_actions(driver)
sid, wid, pid = driver.execute_script("return [sys.SID, sys.WID, sys.PID];")
cid = driver.execute_script("return sys.command_queue;")[0]['cid']
driver.execute_script(f"sys.CID='{cid}';")

print(f"sid:{sid}, wid:{wid}, pid:{pid}, cid:{cid}")

info = {
    'sid': sid,
    'wid': wid,
    'pid': pid,
    'cid': cid,
    'ts': int(round(time.time(), 3) * 1000),
    'start_index': 0
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0',
    'Accept': '*/*',
    'Host': 'platform.epicov.org',
    'Connection': 'keep-alive'
}


query_dict = {
    'sid': info['sid'],
    'wid': info['wid'],
    'pid': info['pid'],
    'ts': info['ts'],
    'mode': 'ajax',
    'data': {
        'queue': [
            {
                'wid': info['wid'],
                'pid': info['pid'],
                'cid': info['cid'],
                'cmd': 'SetPaginating',
                'params': {'start_index': info['start_index'], 'rows_per_page': 27}
            },
            {
                'wid': info['wid'],
                'pid': info['pid'],
                'cid': info['cid'],
                'cmd': 'GetData',
                'params': {}
            }
        ]
    }
}

base_url = "https://platform.epicov.org/epi3/frontend"
url = f"{base_url}?sid={query_dict['sid']}&wid={query_dict['wid']}&pid={query_dict['pid']}&ts={query_dict['ts']}&mode=ajax&data="
queue_data = json.dumps(query_dict['data'])
request_url = url + str(queue_data)

start_index = read_continue_index()

for index in tqdm.tqdm(range(start_index, page_number)):
    save_continue_index(index)
    query_dict['ts'] = int(round(time.time(), 3) * 1000)
    query_dict['data']['queue'][0]['params']['start_index'] = index * 27
    url = f"https://platform.epicov.org/epi3/frontend?sid={query_dict['sid']}&wid={query_dict['wid']}&pid={query_dict['pid']}&ts={query_dict['ts']}&mode=ajax&data="
    queue_data = json.dumps(query_dict['data'])
    request_url = url + str(queue_data)

    response = requests.get(request_url, headers=headers, data={}, proxies=proxies)
    sequence_info = [clean_response(single_info) for single_info in json.loads(response.text)['records']]

    filename = f'GisAid_{index}.json'
    with open(filename, 'w') as file:
        json.dump(sequence_info, file, indent=4)
