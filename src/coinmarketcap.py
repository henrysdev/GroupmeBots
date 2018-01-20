import requests
import json
import string

COIN_DICT = {}
INCLUDED_STATS = ["symbol", "price_usd", "price_btc", "rank",
            "percent_change_1h", "percent_change_24h",
            "percent_change_7d", "24h_volume_usd", "market_cap_usd"]

def fetch_coin_stats(id):
    url = "https://api.coinmarketcap.com/v1/ticker/{}".format(id)
    headers = {"Content-Type": "application/json"}
    resp = requests.get(
        url=url
    )
    json_resp = json.loads(resp.text)
    return json_resp

def update_all_coins():
    global COIN_DICT
    url = "https://api.coinmarketcap.com/v1/ticker"
    headers = {"Content-Type": "application/json"}
    params = dict(
        limit=0
    )
    resp = requests.get(
        url=url,
        headers=headers,
        params=params
    )
    json_resp = json.loads(resp.text)
    for obj in json_resp:
        symb = obj['symbol']
        COIN_DICT[symb] = obj

def check_for_ticker(ticker):
    global COIN_DICT
    if bool(COIN_DICT) == False:
        update_all_coins()
    if ticker in COIN_DICT:
        return True
    else:
        return False

def get_coin_price(ticker):
    price = None
    if ticker in COIN_DICT:
        coin_id = COIN_DICT[ticker]['id']
        price = fetch_coin_stats(coin_id)[0]['price_usd']
        print(price)
    return price

def get_coin_stats(ticker):
    stats = None
    if ticker in COIN_DICT:
        coin_id = COIN_DICT[ticker]['id']
        stats = fetch_coin_stats(coin_id)
    return stats

def prettify_coin_stats(json_stats, data_keys=INCLUDED_STATS):
    data_obj = json_stats[0]
    formed_txt = ""
    for j in data_keys:
        if j in data_obj:
            formed_txt += (j + ": " + str(data_obj[j])) + "\n"
    return formed_txt

def get_top_coins(ranks):
    url = "https://api.coinmarketcap.com/v1/ticker"
    headers = {"Content-Type": "application/json"}
    params = dict(
        limit=ranks
    )
    resp = requests.get(
        url=url,
        headers=headers,
        params=params
    )
    json_resp = json.loads(resp.text)
    return json_resp

