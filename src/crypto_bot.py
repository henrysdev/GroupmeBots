import requests
import json
import datetime
import time
import configparser
import string
import re
import coinmarketcap as cmc_api

BASE_URL = 'https://api.groupme.com/v3'
AUTH_TOKEN = None
GROUP_ID = None
BOT_ID = None
LAST_ID = 0


def execute_command(cmd, args):
    if   cmd == "gupta":
        try:
            send_message("Gupta is a cuck")
            return True
        except:
            print("unable to send message")
            return False
    elif cmd == "price":
        if args is not None:
            ticker = args[0]
        price = cmc_api.get_coin_price(ticker)
        if price is not None:
            try:
                send_message("*{0} Price*\n${1}".format(ticker, price))
                return True
            except:
                print("unable to send messages")
                return False
        else:
            print("unable to retrieve price")
            return False
    elif cmd == "stats":
        if args is not None:
            ticker = args[0]
        stats = cmc_api.get_coin_stats(ticker)
        stats = cmc_api.prettify_coin_stats(stats)
        if stats is not None:
            try:
                send_message("*{0} Stats*\n{1}".format(ticker,stats))
                return True
            except:
                print("unable to send messages")
                return False
        else:
            print("unable to retrieve stats")
            return False
    elif cmd == "top":
        if args is not None:
            ranks = args[0]
        else:
            return False
        top_coins = cmc_api.get_top_coins(ranks)
        msg_str = "*Top {} Coins*\n".format(ranks)
        for coin in top_coins:
            print(coin)
            coin_summ = cmc_api.prettify_coin_stats([coin], ["name","rank","price_usd"])
            msg_str += coin_summ + '\n'
        try:
            send_message(msg_str)
            return True
        except:
            print("unable to send message")
            return False

# check to see if exists on coinmarketcap as well
def validate_ticker(ticker):
    regex = r"([A-z]{3,5})"
    match_obj = re.match(regex, ticker)
    if match_obj is not None:
        if cmc_api.check_for_ticker(ticker):
            print("√ ticker checks out")
            return True
    print("ticker does not check out")
    return False

def validate_input(cmd, args):
    cmd = cmd.lower()
    if cmd   == "gupta":
        if args == None:
            return True
    elif cmd == "price":
        if validate_ticker(args[0]):
            return True
    elif cmd == "stats":
        if validate_ticker(args[0]):
            return True
    elif cmd == "top":
        try:
            ranks = int(args[0])
            if ranks <= 100:
                return True
        except:
            print("invalid argument")
            return False
    return False

def parse_for_commands(msg):
    regex = r"(![A-z]{3,5})(( [A-z\d]+){1,5})*"
    r = re.compile(regex)
    res = r.match(msg['text'])
    if res is not None:
        cmd = res.group(1)[1:]
        if res.group(2) is not None:
            args = res.group(2).split()
        else:
            args = None
        print("cmd: {}".format(cmd))
        print("args: {}".format(args))
        print('\n')
        if validate_input(cmd, args):
            print("√ command input checks out")
            execute_command(cmd, args)
    else:
        print("no commands found")

def refresh_messages():
    global LAST_ID
    url = '{0}/groups/{1}/messages'.format(BASE_URL, GROUP_ID)
    headers = {"Content-Type": "application/json"}
    params = dict(
        after_id=LAST_ID,
        token=AUTH_TOKEN
    )
    resp = requests.get(
        url=url,
        headers=headers,
        params=params 
    )
    try:
        json_resp = json.loads(resp.text)
    except:
        print("unable to parse")
        return
    fetched_msgs = json_resp['response']['messages']
    if len(fetched_msgs) > 0:
        for msg in fetched_msgs:
            parse_for_commands(msg)
        LAST_ID = fetched_msgs[0]['id']

def send_message(message):
    url = '{0}/bots/post'.format(BASE_URL)
    j_data = {"bot_id": BOT_ID, "text": message}
    j_data = json.JSONEncoder().encode(j_data)
    headers = {"Content-Type": "application/json"}
    params = dict(
        token=AUTH_TOKEN
    )
    resp = requests.post(
        url=url, 
        data=j_data,
        headers=headers,
        params=params
    )
    print(resp.text)

def get_last_message_id():
    url = '{0}/groups/{1}/messages'.format(BASE_URL, GROUP_ID)
    headers = {"Content-Type": "application/json"}
    params = dict(
        limit=1,
        token=AUTH_TOKEN
    )
    resp = requests.get(
        url=url,
        headers=headers,
        params=params 
    )
    json_resp = json.loads(resp.text)
    last_id = json_resp['response']['messages'][0]['id']
    return last_id

def load_config():
    global AUTH_TOKEN
    global BOT_ID
    global GROUP_ID
    config = configparser.ConfigParser()
    config.read('config.ini')
    AUTH_TOKEN = config['CREDENTIALS']['auth_token']
    GROUP_ID = config['IDENTIFIERS']['dev_group_id']
    BOT_ID = config['IDENTIFIERS']['dev_bot_id']

def init_bot():
    global LAST_ID
    LAST_ID = get_last_message_id()

def main_loop():
    while True:
        refresh_messages()

if __name__ == "__main__":
    load_config()
    init_bot()
    main_loop()