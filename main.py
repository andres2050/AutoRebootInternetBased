import requests
from time import sleep
import json
import subprocess
from datetime import datetime


def timestamped_print(*args, **kwargs):
    print(datetime.now(), *args, **kwargs)


def connected_to_internet(url, timeout):
    try:
        _ = requests.head(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        print('No internet connection available.')
    return False


def is_valid_number(n):
    return (type(n) is int or type(n) is float) and n > 0


def is_valid_configs(c):
    if not c:
        timestamped_print('configs.json not exist.')
        return False
    elif 'webpages' not in c or len(c['webpages']) == 0:
        timestamped_print('Invalid webpages.')
        return False
    elif 'timeout' not in c or not is_valid_number(c['timeout']):
        timestamped_print('Invalid timeout')
        return False
    elif 'sleep-time' not in c or not is_valid_number(c['sleep-time']):
        timestamped_print('Invalid sleep-time')
        return False
    elif 'interface' not in c or c['interface'] == '':
        timestamped_print('invalid interface')

    return True


if __name__ == '__main__':
    internetFails = 0
    checkMinerFails = 0
    while True:
        configs = {}
        try:
            with open('./configs.json', 'r') as f:
                configs = json.load(f)
        except IOError:
            timestamped_print('File not accessible')
            break

        if is_valid_configs(configs):
            there_is_internet = False
            for page in configs['webpages']:
                if connected_to_internet(page, configs['timeout']):
                    there_is_internet = True
                    break

            if not there_is_internet:
                subprocess.run(['ifconfig', configs['interface'], 'up'])
                sleep(1)
                subprocess.run(['ifconfig', configs['interface'], 'down'])
                timestamped_print('restart', configs['interface'])
                internetFails+1
            else:
                timestamped_print("Internet works great.")
                internetFails = 0

            if internetFails * configs['sleep-time'] >= configs['self-restart-time']:
                subprocess.run(['reboot', 'now'])

        sleep(configs['sleep-time'])
