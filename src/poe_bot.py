import requests
import json
import datetime
import time
import random
import configparser
import string

BASE_URL = 'https://api.groupme.com/v3'
MAIN_DELAY = 86400 # 24 hours
WATCHDOG_DELAY = 300 # 5 minutes
NUM_INCREMENTS = MAIN_DELAY / WATCHDOG_DELAY # 144 watchdog cycles for 1 main cycle
AUTH_TOKEN = None
BOT_ID = None
PRICE_ALERT_THRESHOLD = 8.0


def get_curr_time():
    now = datetime.datetime.now()
    # formed_txt = now.strftime('%Y-%m-%d %I:%M%p')
    formed_txt = now.strftime('%Y-%m-%d')
    return formed_txt


def prettify_stats(resp_data):
    data_obj = resp_data[0]
    data_keys = ["symbol", "price_usd", "price_btc", "percent_change_1h", "percent_change_24h", "rank", "market_cap_usd"]
    formed_txt = ""
    for j in data_keys:
        if j in data_obj:
            formed_txt += (j + ": " + str(data_obj[j])) + "\n"
    return formed_txt


def scrape_stats():
    url = "https://api.coinmarketcap.com/v1/ticker/poet/"
    resp = requests.get(url)
    resp_data = json.loads(resp.text)
    #parsed_change = parse_stats(resp_data, 'percent_change_1h')
    return resp_data


def detect_price_breakout():
    poe_data = scrape_stats()[0]
    curr_change = float(poe_data["percent_change_1h"])
    print("curr_change: " + str(curr_change))
    if abs(curr_change) >= PRICE_ALERT_THRESHOLD:
        return True
    else:
        return False


def send_message(message):
    url = '{0}/bots/post'.format(BASE_URL)
    j_data = {"bot_id": BOT_ID, "text": message}
    j_data = json.JSONEncoder().encode(j_data)
    headers = {"Content-Type": "application/json"}
    params = dict(
        token=AUTH_TOKEN
    )
    resp = requests.post(url=url, 
        data=j_data, 
        params=params, 
        headers=headers
    )
    print(resp.text)


def main_loop():
    i = 0
    last_movement_i = 0
    while True:
        if i % NUM_INCREMENTS == 0 and i is not 0:
            message_header = "Upoedate " + get_curr_time()
            stats = scrape_stats()
            pretty_stats = prettify_stats(stats)
            if message_header is not None:
                print(message_header)
                send_message(message_header)
            if pretty_stats is not None:
                print(pretty_stats)
                send_message(pretty_stats)

        time.sleep(WATCHDOG_DELAY)
        if abs(i - last_movement_i) >= 12: # 12 5-minute increments in one hour
            if detect_price_breakout(): # trip watchdog if price has changed dramatically
                message_header = "*Price Movement Alert* "
                stats = scrape_stats()
                pretty_stats = prettify_stats(stats)
                if message_header is not None:
                    print(message_header)
                    send_message(message_header)
                if pretty_stats is not None:
                    print(pretty_stats)
                    send_message(pretty_stats)
                last_movement_i = i
        i+=1


def load_config():
    global AUTH_TOKEN
    global BOT_ID
    config = configparser.ConfigParser()
    config.read('config.ini')
    AUTH_TOKEN = config['CREDENTIALS']['auth_token']
    BOT_ID = config['IDENTIFIERS']['dev_bot_id']


if __name__ == "__main__":
    load_config()
    if AUTH_TOKEN is not None:
        main_loop()
    else:
        print("No auth_token. Exiting")
        exit()
