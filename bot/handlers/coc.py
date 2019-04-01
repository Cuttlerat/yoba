from services.crypto_compare import CryptoCompare
from logger import log_print
import requests
import json
from models.models import connector, ClashExclude, Pingers
from sqlalchemy import and_

def coc(config, bot, update):
    last_game={}
    r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/createPrivateClash',
        headers={"content-type":"application/json;charset=UTF-8",
                 "cookie":"remcg={}".format(config.coc_remcg())},
        data='[{}, {{"SHORT":true}}]'.format(config.coc_secret()))

    if r.status_code == 200:

        with connector(config.engine()) as ses:
            all_matches = ses.query(Pingers.username).filter(Pingers.chat_id == update.message.chat_id).order_by(Pingers.username).distinct().all()
            exclude = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            users = [ x for x in all_matches if x not in exclude ]
            users = [ x for x in users for x in x ]
            out_text = ""
        coc_id = json.loads(r.text)["success"]["publicHandle"]
        message = """
Please send /coc_disable if you don't want to be notified about new CoC games

https://www.codingame.com/clashofcode/clash/{coc_id}

{users}
        """.format(coc_id=coc_id, users=" ".join(["@{}".format(user) for user in users]))
        last_game["coc_id"] = coc_id
    else:
        coc_id = "Error"
        message = "Something went wrong..."

    sent = bot.send_message(chat_id=update.message.chat_id,
                     text=message)
    last_game["message_id"] = sent.message_id

    with open("/tmp/coc_{}".format(update.message.chat_id), "w") as file:
        file.write(json.dumps(last_game)) 


    log_print('Clash of Code "{}"'.format(coc_id))


def coc_start(config, bot, update):

    try:
        with open("/tmp/coc_{}".format(update.message.chat_id), "r") as file:
            last_game = json.loads(file.read())
    except IOError:
        last_game = {"coc_id":"", "message_id":""}

    if last_game["coc_id"]:
        r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/startClashByHandle',
            headers={"content-type":"application/json;charset=UTF-8",
                     "cookie":"remcg={}".format(config.coc_remcg())},
            data='[{coc_secret}, "{coc_id}"]'.format(coc_secret=config.coc_secret(),
                coc_id=last_game["coc_id"]))

        if r.status_code == 200:
            message = 'CoC is about to start! Hurry up!'
        else:
            message = 'Could not start "{}" CoC game...'
    else:
        last_game["coc_id"] = "None"
        message = "Could not find last CoC id"

    if last_game["message_id"]:
        bot.send_message(chat_id=update.message.chat_id,
                         reply_to_message_id=last_game["message_id"],
                         text=message,
                         parse_mode="markdown")
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text=message,
                         parse_mode="markdown")
    if last_game["coc_id"] != "None":
        log_print('Clash of Code "{}" started'.format(last_game["coc_id"]))


def coc_disable(config, bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if not username:
        msg = "You don't have username"
    else:
        with connector(config.engine()) as ses:
            all_excludes = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            all_excludes = [ x for x in all_excludes for x in x ]
            if username in all_excludes:
                msg = "You are already excluded"
            else:
                exclude = ClashExclude( 
                        username=username,
                        chat_id=chat_id)
                ses.add(exclude)
                msg = "You won't get any CoC notifications anymore. You can enable notifcations by /coc_enable"
    bot.send_message(chat_id=update.message.chat_id,
            reply_to_message_id=message_id,
            text=msg)
    log_print('Clash of Code enable', username)

def coc_enable(config, bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if not username:
        msg = "You don't have username"
    else:
        with connector(config.engine()) as ses:
            all_excludes = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            all_excludes = [ x for x in all_excludes for x in x ]
            if username in all_excludes:
                ses.query(ClashExclude).filter(and_(
                    ClashExclude.chat_id == chat_id,
                    ClashExclude.username == username)).delete()
                msg = "You will get CoC notifications now!"
            else:
                msg = "You are already excluded"
    bot.send_message(chat_id=update.message.chat_id,
            reply_to_message_id=message_id,
            text=msg,
            parse_mode="markdown")
    log_print('Clash of Code disable', username)

