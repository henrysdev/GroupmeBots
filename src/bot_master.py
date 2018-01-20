import requests
import json
import datetime
import time
import random
import configparser
import string

BASE_URL = 'https://api.groupme.com/v3'

class Bot (object):
    def __init__(self, name, bot_id, group_id, avatar_url, callback_url):
        self.name = name
        self.bot_id = bot_id
        self.group_id = group_id
        self.avatar_url = avatar_url
        self.callback_url = callback_url
        self.creation_time = datetime.datetime.now()

    def __str__(self):
        str_rep = ""
        str_rep += "name: " + str(self.name) + "\n"
        str_rep += "bot_id: " + str(self.bot_id) + "\n"
        str_rep += "group_id: " + str(self.group_id) + "\n"
        str_rep += "avatar_url: " + str(self.avatar_url) + "\n"
        str_rep += "callback_url: " + str(self.callback_url) + "\n"
        str_rep += "creation_time: " + str(self.creation_time) + "\n"
        return str_rep


""" Utility Functions """
def get_auth_token():
    config = configparser.ConfigParser()
    config.read('config.ini')
    auth_token = config['CREDENTIALS']['auth_token']
    return auth_token

def rand_callback_url():
    rand_site = ''.join(random.choices(string.ascii_lowercase, k=4))
    rand_path = ''.join(random.choices(string.ascii_lowercase, k=16))
    dummy_url = "https://{}.com/{}".format(rand_site, rand_path)
    return dummy_url
""" """


def get_list_of_active_bots():
    bots = []
    url = '{0}/bots'.format(BASE_URL)
    params = dict(
        token=get_auth_token()
    )
    try:
        resp = requests.get(url=url, params=params)
        resp_data = json.loads(resp.text)
    except:
        print("failed GET request")
        return None
    try:
        bots_list = resp_data["response"]
        for bot in bots_list:
            name = bot["name"]
            bot_id = bot["bot_id"]
            group_id = bot["group_id"]
            avatar_url = bot["avatar_url"]
            callback_url = bot["callback_url"]
            new_bot = Bot(name=name, 
                bot_id=bot_id, 
                group_id=group_id, 
                avatar_url=avatar_url, 
                callback_url=callback_url
            )
            bots.append(new_bot)
        return bots
    except:
        print("Couldn't parse any bots")
        print(resp_data)
        return None


def delete_bot(bot_id):
    url = '{0}/bots/destroy'.format(BASE_URL)
    params = dict(
        token=get_auth_token(),
        bot_id=bot_id
    )
    resp = requests.post(url=url, params=params)


def create_bot(bot_name, group_id, avatar_url, callback_url, auth_token):
    url = '{0}/bots'.format(BASE_URL)
    j_data = {"bot": { "name": bot_name, "group_id": group_id, "callback_url": callback_url, "avatar_url": avatar_url}}
    j_data = json.JSONEncoder().encode(j_data)
    headers = {"Content-Type": "application/json"}
    params = dict(
        token=auth_token
    )
    try:
        resp = requests.post(url=url, 
            data=j_data, 
            params=params, 
            headers=headers
        )
        resp_data = json.loads(resp.text)
    except:
        print("failed POST request")
        return None
    try:
        bot_id = resp_data["response"]["bot"]["bot_id"]
        new_bot = Bot(bot_name, bot_id, group_id, avatar_url, callback_url)
        return new_bot
    except:
        print("Couldn't create new bot :/")
        print(resp_data)
        return None


def send_message(bot_id, msg=""):
    url = '{0}/bots/post'.format(BASE_URL)
    # message only
    j_data = {"bot_id": bot_id, "text": msg}
    j_data = json.JSONEncoder().encode(j_data)
    headers = {"Content-Type": "application/json"}
    params = dict(
        token=get_auth_token()
    )
    resp = requests.post(url=url, data=j_data, params=params, headers=headers)
    print(resp.text)


def create_bot_ui():
    menu_ui = """
    Create Bot Menu
    0 - Create Bot from config.ini
    1 - Create Bot Manually
    2 - Back to Main Menu
    """
    while True:
        print(menu_ui)
        selection = input("> ")
        if selection == "0":
            auth_token = get_auth_token()
            config = configparser.ConfigParser()
            config.read('config.ini')
            bot_cfg = config['DEFAULT']
            bot_name = bot_cfg['bot_name']
            group_id = bot_cfg['group_id']
            avatar_url = bot_cfg['avatar_url']
            #callback_url = bot_cfg['callback_url']
            callback_url = rand_callback_url()
            bot = create_bot(
                bot_name=bot_name, 
                group_id=group_id, 
                avatar_url=avatar_url, 
                callback_url=callback_url, 
                auth_token=auth_token
            )
            if bot == None:
                print("unable to create bot. Start over bot creation")
            else:
                print("Successfully created bot")
                print(bot)
                break

        elif selection == "1":
            auth_token = get_auth_token()
            while True:
                bot_name = input("bot name: ")
                if len(bot_name) == 0:
                    print("invalid bot name. Start over bot creation")
                    continue
                group_id = input("group id: ")
                if len(bot_name) == 0:
                    print("invalid group_id. Start over bot creation")
                    continue
                avatar_url = input("avatar_url: ")
                if len(bot_name) == 0:
                    print("invalid avatar_url. Start over bot creation")
                    continue
                #callback_url = input("callback_url: ")
                callback_url = rand_callback_url()
                if len(callback_url) == 0:
                    print("invalid callback_url. Start over bot creation")
                    continue
                else:
                    bot = create_bot(
                        bot_name=bot_name, 
                        group_id=group_id, 
                        avatar_url=avatar_url, 
                        callback_url=callback_url, 
                        auth_token=auth_token
                    )
                    if bot == None:
                        print("unable to create bot. Start over bot creation")
                    else:
                        print("Successfully created bot")
                        print(bot)
                        break
            break

        else:
            return


def manage_bots_ui():
    menu_ui = """
    Manage Existing Bots Menu
    0 - See List of Created Bots
    1 - Delete Bot by bot_id
    2 - Back to Main Menu
    """
    while True:
        print(menu_ui)
        selection = input("> ")
        if selection == "0":
            print("\n**Active Bots**\n")
            bots = get_list_of_active_bots()
            for bot in bots:
                print(bot)
            print("***************")
        elif selection == "1":
            print("Delete bot by bot_id")
            bot_id = input("> ")
            delete_bot(bot_id)
        else:
            return


def send_message_ui():
    menu_ui = """
    Send Message Menu
    0 - Send Message as Bot
    1 - Back to Main Menu
    """
    while True:
        print(menu_ui)
        selection = input("> ")
        if selection == "0":
            print("Send Message as Bot")
            print("enter bot_id to send from")
            bot_id = input("> ")
            print("enter Message to send")
            message = input("> ")
            try:
                send_message(bot_id=bot_id, msg=message)
            except:
                print("unable to send message")
        else:
            return


# Main Menu control loop
def main_ui():
    menu_ui = """
    Main Menu
    0 - Create New Bot
    1 - Send Message
    2 - Manage Existing Bots
    3 - Exit
    """
    while True:
        print(menu_ui)
        selection = input("> ")
        if selection == "0":
            create_bot_ui()
        elif selection == "1":
            send_message_ui()
        elif selection == "2":
            manage_bots_ui()
        else:
            exit(0)


if __name__ == "__main__":
    main_ui()