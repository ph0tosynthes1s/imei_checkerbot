import json
import requests
import time
import xmltodict
from db import Database
import re
import keys
import asyncio
import cloudscraper
import xml.etree.ElementTree as ET
import urllib.request

db = Database('database.db')

#подключение к АПИ
def connect_api(imei_code,service_code):
    url = 'https://api.ifreeicloud.co.uk'
    values = {'key': keys.API_IFREE,
                'service': service_code,
                'imei': imei_code,
              }
    data = urllib.parse.urlencode(values).encode("utf-8")
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    page = response.read()
    api_return = json.loads(page)
    return api_return

#проверка услуги АПИ
def check_api(imei_code, service_code):
    answer = connect_api(imei_code, service_code)
    if not answer["success"]:
        final_response = '❌Вы ввели неправильный IMEI или серийный номер!'
    else:
        final = answer["response"].replace("<br>", "\n")
        result = re.sub('<[^<]+?>', '', final)
        final_response = result
    print(final_response)
    return final_response


#проверка статуса
def req_check(apikey, server_id):
    req_check = f"""<?xml version='1.0' encoding='utf-8'?>
    <check apikey="{apikey}">
        <sms server_id="{server_id}" />
    </check>"""
    headers = {'Content-Type': 'application/xml'}
    req_check_response = requests.post('https://smspilot.ru/api2.php', data=req_check, headers=headers).text
    req_check_parse = xmltodict.parse(req_check_response)
    req_check_dump = json.dumps(req_check_parse)
    req_check_load = json.loads(req_check_dump)
    status = req_check_load['check']['sms']['@status']
    return status

#проверка статуса ping
async def ping_status_check(apikey, server_id, status, phone, operator):
    while int(status)== 0  or int(status) == 1 :
        print(status)
        status = req_check(apikey, server_id)
        await asyncio.sleep(10)
        if int(status)== 2:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: В сети'
            return result
        if int(status)== -1:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Не в сети'
            return result
        if int(status) == -2:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Ошибка!'
            return result

#проверка статуса hlr
async def hlr_status_check(apikey, server_id, status, phone, operator):
    while int(status)== 0  or int(status) == 1 :
        print(status)
        status = req_check(apikey, server_id)
        await asyncio.sleep(10)
        if int(status)== 2:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Обслуживается'
            return result
        if int(status)== -1:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Не обслуживается'
            return result
        if int(status) == -2:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Ошибка!'
            return result

async def hlr_status_check(apikey, server_id, status, phone, operator):
    while int(status)== 0  or int(status) == 1 :
        print(status)
        status = req_check(apikey, server_id)
        await asyncio.sleep(10)
        if int(status)== 2:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Обслуживается'
            return result
        if int(status)== -1:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Не обслуживается'
            return result
        if int(status) == -2:
            result = f'Номер телефона: {phone}\nОператор: {operator}\nСтатус: Ошибка!'
            return result

#проверка 3gsm
def gsm_req_check(id):
    scraper = cloudscraper.create_scraper()
    arr = {}
    arr['ID'] = id
    xmlData = ET.Element('PARAMETERS')
    for key, val in arr.items():
        key = key.upper()
        ET.SubElement(xmlData, key).text = str(val)
    data = {
        'username': keys.USERNAME,
        'apiaccesskey': keys.API_ACCESS_KEY,
        'action': 'getimeiorder',
        'requestformat': keys.REQUESTFORMAT,
        'parameters': ET.tostring(xmlData, encoding='unicode')
    }
    headers = {
        'User-Agent': scraper.headers['User-Agent']
    }
    req_response = scraper.post(keys.DHRUFUSION_URL + '/api/index.php', data=data, headers=headers)
    req_load = json.loads(req_response.text)
    return req_load

async def gsm_status_check(status,id):
    while int(status)== 0  or int(status) == 1 :
        print(status)
        get = gsm_req_check(id)
        status = get['SUCCESS'][0]['STATUS']
        await asyncio.sleep(10)
        if int(status) == 4:
            print(status)
            return get

#функция fmi_s1
def fmi_s1(imei_code, user_id, date):
    result = check_api(imei_code, 4)
    return result
#функция clean_lostS2
def clean_lostS1(imei_code, user_id, date):
    result = check_api(imei_code, 60)
    return result
#функция basic_info
def basic_info(imei_code, user_id, date):
    result = check_api(imei_code, 120)
    return result
#функция sold_by
def sold_by(imei_code, user_id, date):
    result = check_api(imei_code, 282)
    return result
#функция balance
def balance():
    url = 'https://api.ifreeicloud.co.uk'
    values = {'key': '9NX-KVR-UI2-QV1-X2N-TN1-GW6-JIH',
                'accountinfo': 'balance',
              }
    data = urllib.parse.urlencode(values).encode("utf-8")
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    page = response.read()
    x = json.loads(page)
    result = f"Баланс iFree: {x['object']['account_balance']}$"
    return result

async def dhru():
    scraper = cloudscraper.create_scraper()
    arr = {}
    arr['IMEI'] = '356281920502180'
    arr['ID'] = '86'
    xmlData = ET.Element('PARAMETERS')
    for key, val in arr.items():
        key = key.upper()
        ET.SubElement(xmlData, key).text = str(val)
    data = {
        'username': keys.USERNAME,
        'apiaccesskey': keys.API_ACCESS_KEY,
        'action': 'placeimeiorder',
        'requestformat': keys.REQUESTFORMAT,
        'parameters': ET.tostring(xmlData, encoding='unicode')
    }
    print(data)
    headers = {
        'User-Agent': scraper.headers['User-Agent']
    }
    req_response = scraper.post(keys.DHRUFUSION_URL + '/api/index.php', data=data, headers=headers)
    req_load = json.loads(req_response.text)
    print(req_load)
    if 'ERROR' in req_load:
        result = 'Вы ввели неправильный IMEI'
        return result
    else:
        id = req_load['SUCCESS'][0]['REFERENCEID']
        status = gsm_req_check(id)
        status_get = status['SUCCESS'][0]['STATUS']
        print(status_get)
        result = await gsm_status_check(int(status_get),id)
        print(result['SUCCESS'])
        return result['SUCCESS']


