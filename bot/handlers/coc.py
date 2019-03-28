from services.crypto_compare import CryptoCompare
from logger import log_print
import requests
import json

def coc(config, bot, update):
    r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/createPrivateClash',
        headers={"content-type":"application/json;charset=UTF-8",
                 "cookie":"remcg={}".format(config.coc_remcg())},
        data='[{}, {{"SHORT":true}}]'.format(config.coc_secret()))

    if r.status_code == 200:
        coc_id = json.loads(r.text)["success"]["publicHandle"]
        message = "https://www.codingame.com/clashofcode/clash/{}".format(coc_id)
        with open("/tmp/coc_last", "w") as file:
            file.write(coc_id)
    else:
        coc_id = "Error"
        message = "Something went wrong..."

    sent = bot.send_message(chat_id=update.message.chat_id,
                     text=message,
                     parse_mode="markdown")
    with open("/tmp/coc_last_message_id", "w") as file:
        file.write(str(sent.message_id)) 


    log_print('Clash of Code "{}"'.format(coc_id))


def coc_start(config, bot, update):
    with open("/tmp/coc_last", "r") as file:
        coc_id = file.read()
    with open("/tmp/coc_last_message_id", "r") as file:
        coc_msg_id = int(file.read())
    if coc_id:
        r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/startClashByHandle',
            headers={"content-type":"application/json;charset=UTF-8",
                     "cookie":"remcg={}".format(config.coc_remcg())},
            data='[{coc_secret}, "{coc_id}"]'.format(coc_secret=config.coc_secret(),
                coc_id=coc_id))

        if r.status_code == 200:
            message = 'CoC is about to start! Hurry up!'
        else:
            message = 'Could not start "{}" CoC game...'
    else:
        coc_id = "None"
        message = "Could not find last CoC id"

    if coc_msg_id:
        bot.send_message(chat_id=update.message.chat_id,
                         reply_to_message_id=coc_msg_id,
                         text=message,
                         parse_mode="markdown")
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text=message,
                         parse_mode="markdown")
    log_print('Clash of Code "{}" started'.format(coc_id))
