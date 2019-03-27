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
    else:
        coc_id = "Error"
        message = "Something went wrong..."

    bot.send_message(chat_id=update.message.chat_id,
                     text=message,
                     parse_mode="markdown")
    log_print('Clash of Code "{}"'.format(coc_id))
