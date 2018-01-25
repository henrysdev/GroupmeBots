import requests
import json
import datetime
import time
import configparser
import string
import re
import sys
import coinmarketcap as cmc_api

# globals
BASE_URL = 'https://api.groupme.com/v3'
AUTH_TOKEN = None
GROUP_ID = None
BOT_ID = None
LOGGER_BOT_ID = None
LAST_ID = 0
RANKS_LIMIT = 5


# carry out approved command 
def execute_command(cmd, args):
    if cmd == "help":
        try:
            msg_txt = "POEbot Commands List\n\n"
            msg_txt += "!price <ticker>\n"
            msg_txt += "!stats <ticker>\n"
            msg_txt += "!top <# top coins>\n"
            msg_txt += "!help"
            send_message(msg_txt)
            return True
        except:
            logger("unable to send Price messages")
            return False
    if cmd == "price":
        if args is not None:
            ticker = args[0]
        else:
            logger("unable to send Price messages")
            return False
        price = cmc_api.get_coin_price(ticker)
        if price is not None:
            try:
                msg_txt = "{0} Price\n${1}".format(ticker, price)
                send_message(msg_txt)
                return True
            except:
                logger("unable to send Price messages")
                return False
        else:
            logger("unable to retrieve price")
            return False
    elif cmd == "stats":
        if args is not None:
            ticker = args[0]
        else:
            logger("unable to send Stats messages")
            return False
        stats = cmc_api.get_coin_stats(ticker)
        stats = cmc_api.prettify_coin_stats(stats)
        if stats is not None:
            try:
                msg_txt = "{0} Stats\n{1}".format(ticker,stats)
                send_message(msg_txt)
                return True
            except:
                logger("unable to send Stats messages")
                return False
        else:
            logger("unable to retrieve stats")
            return False
    elif cmd == "top":
        if args is not None:
            ranks = args[0]
        else:
            return False
        top_coins = cmc_api.get_top_coins(ranks)
        msg_str = "Top {} Coins\n".format(ranks)
        for coin in top_coins:
            logger(coin)
            coin_summ = cmc_api.prettify_coin_stats([coin], ["name","rank","price_usd"])
            msg_str += coin_summ + '\n'
        try:
            send_message(msg_str)
            return True
        except:
            logger("unable to send message")
            return False

# check to see if exists on coinmarketcap as well
def validate_ticker(ticker):
    regex = r"([A-z]{3,5})"
    match_obj = re.match(regex, ticker)
    if match_obj is not None:
        if cmc_api.check_for_ticker(ticker):
            logger("√ ticker checks out")
            return True
    logger("ticker does not check out")
    return False

# check to ensure valid commands are being passed
def validate_input(cmd, args):
    if cmd   == "help":
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
            if ranks <= RANKS_LIMIT:
                return True
        except:
            logger("invalid argument")
            return False
    return False

# ensure that commands and arguments are of the right format
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
        logger("cmd: {}".format(cmd))
        logger("args: {}".format(args))
        logger('\n')
        cmd = cmd.lower()
        if args is not None or cmd == "help":
            if validate_input(cmd, args):
                logger("√ command input checks out")
                execute_command(cmd, args)

# update function that checks new messages for commands
def refresh_messages():
    global LAST_ID
    url = '{0}/groups/{1}/messages'.format(BASE_URL, GROUP_ID)
    headers = {"Content-Type": "application/json"}
    params = dict(
        after_id=LAST_ID,
        token=AUTH_TOKEN
    )
    try:
        resp = requests.get(
            url=url,
            headers=headers,
            params=params 
        )
    except:
        logger("http GET request failed [refresh_messages]")
        return
    try:
        json_resp = json.loads(resp.text)
    except:
        logger("unable to parse into json")
        return
    if json_resp is not None:
        try:
            fetched_msgs = json_resp['response']['messages']
            if len(fetched_msgs) > 0:
                for msg in fetched_msgs:
                    parse_for_commands(msg)
                LAST_ID = fetched_msgs[0]['id']
        except:
            return
    else:
        logger("json not subscriptable")
        return

# debugging module
def logger(message):
    print(message)
    #send_message(message, logging=True)

# sends message to GroupMe group
def send_message(message, logging=False):
    bot_id = BOT_ID
    if logging:
        bot_id = LOGGER_BOT_ID
    url = '{0}/bots/post'.format(BASE_URL)
    j_data = {"bot_id": bot_id, "text": message}
    j_data = json.JSONEncoder().encode(j_data)
    headers = {"Content-Type": "application/json"}
    params = dict(
        token=AUTH_TOKEN
    )
    try:
        resp = requests.post(
            url=url, 
            data=j_data,
            headers=headers,
            params=params
        )
        if logging:
            print(resp.text)
        else:
            logger(resp.text)
    except:
        if logging:
            print("Log http POST request failed")
        else:
            logger("http POST request failed")

# obtain the id for the last message sent in a group
def get_last_message_id():
    url = '{0}/groups/{1}/messages'.format(BASE_URL, GROUP_ID)
    headers = {"Content-Type": "application/json"}
    params = dict(
        limit=1,
        token=AUTH_TOKEN
    )
    try:
        resp = requests.get(
            url=url,
            headers=headers,
            params=params 
        )
        json_resp = json.loads(resp.text)
        last_id = json_resp['response']['messages'][0]['id']
        return last_id
    except:
        logger("http GET request failed [get_last_message_id]")
        return None

# load in parameters from config file
def load_config(mode):
    global AUTH_TOKEN
    global BOT_ID
    global GROUP_ID
    global LOGGER_BOT_ID
    config = configparser.ConfigParser()
    config.read('config.ini')
    AUTH_TOKEN = config['CREDENTIALS']['auth_token']
    if mode == "DEV":
        GROUP_ID = config['IDENTIFIERS']['dev_group_id']
        BOT_ID = config['IDENTIFIERS']['dev_bot_id']
    elif mode == "PROD":
        GROUP_ID = config['IDENTIFIERS']['prod_group_id']
        BOT_ID = config['IDENTIFIERS']['prod_bot_id']
    LOGGER_BOT_ID = config['IDENTIFIERS']['logger_bot_id']

# start function for preprocessing
def init_bot():
    global LAST_ID
    LAST_ID = get_last_message_id()

# main update container function
def main_loop():
    while True:
        refresh_messages()

if __name__ == "__main__":
    mode = "DEV"
    if len(sys.argv) > 1:
        if sys.argv[1] == "1":
            mode = "PROD"
    logger("mode: {}".format(mode))
    load_config(mode)
    init_bot()
    main_loop()