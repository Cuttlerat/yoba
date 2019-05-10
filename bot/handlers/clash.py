from logger import log_print
import requests
import json
from models.models import connector, ClashExclude, Pingers
from sqlalchemy import and_
import datetime
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont

def clash(config, bot, update):
    last_game={}
    username = update.message.from_user.username

    r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/createPrivateClash',
        headers={"content-type":"application/json;charset=UTF-8",
                 "cookie":"remcg={remcg};rememberMe={remember_me};cgSession={cg_session}".format(
                     remcg=config.clash_remcg(),
                     remember_me=config.clash_remember_me(),
                     cg_session=config.clash_cg_session())},
        data='[{}, {{"SHORT":true}}]'.format(config.clash_secret()))

    if r.status_code == 200:

        with connector(config.engine()) as ses:
            all_matches = ses.query(Pingers.username).filter(Pingers.chat_id == update.message.chat_id).order_by(Pingers.username).distinct().all()
            exclude = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            users = [ x for x in all_matches if x not in exclude ]
            users = [ x for x in users for x in x ]
            out_text = ""
        clash_id = json.loads(r.text)["success"]["publicHandle"]
        users=" ".join(["@{}".format(user) for user in users])
        message = """
Clash of Code!

https://www.codingame.com/clashofcode/clash/{clash_id}

{users}

Please send /clash_disable if you don't want to receive these notifications
        """.format(clash_id=clash_id, users=users)
        last_game["clash_id"] = clash_id
    else:
        clash_id = "Error"
        message = "Something went wrong..."

    sent = bot.send_message(chat_id=update.message.chat_id,
                     text=message)
    last_game["users"] = users
    last_game["username"] = username
    last_game["message_id"] = sent.message_id

    with open("/tmp/clash_{}".format(update.message.chat_id), "w") as file:
        file.write(json.dumps(last_game)) 


    log_print('Clash of Code "{}"'.format(clash_id))


def clash_start(config, bot, update):

    username = update.message.from_user.username

    try:
        with open("/tmp/clash_{}".format(update.message.chat_id), "r") as file:
            last_game = json.loads(file.read())
    except IOError:
        last_game = {"clash_id":"", "message_id":"", "username": username}

    if last_game["clash_id"]:
        if last_game["username"] == username:
            r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/startClashByHandle',
                headers={"content-type":"application/json;charset=UTF-8",
                         "cookie":"remcg={remcg};rememberMe={remember_me};cgSession={cg_session}".format(
                             remcg=config.clash_remcg(),
                             remember_me=config.clash_remember_me(),
                             cg_session=config.clash_cg_session())},
                data='[{clash_secret}, "{clash_id}"]'.format(clash_secret=config.clash_secret(),
                    clash_id=last_game["clash_id"]))

            if r.status_code == 200:
                message="The game is about to start, hurry up!"
                if last_game["users"]:
                    message = '{users}\n\n{msg}'.format(
                        users=last_game["users"],
                        msg=message)
                log_print('Clash of Code "{}" started'.format(last_game["clash_id"]))
            else:
                message = 'Could not start "{}" Clash game...'.format(
                    last_game["clash_id"])
                log_print(message)
        else:
            last_game["message_id"] = update.message.message_id
            message = 'Only @{} is allowed to start the game'.format(last_game["username"])
    else:
        last_game["clash_id"] = "None"
        message = "Could not find the last Clash id"

    if last_game["message_id"]:
        bot.send_message(chat_id=update.message.chat_id,
                         reply_to_message_id=last_game["message_id"],
                         text=message,
                         parse_mode="markdown")
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text=message,
                         parse_mode="markdown")


def clash_disable(config, bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if not username:
        msg = "The unnamed ones are free from these silly humans vanity"
    else:
        with connector(config.engine()) as ses:
            all_excludes = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            all_excludes = [ x for x in all_excludes for x in x ]
            if username in all_excludes:
                msg = "You've already disabled notifications"
            else:
                exclude = ClashExclude( 
                        username=username,
                        chat_id=chat_id)
                ses.add(exclude)
                msg = "Now you won't receive any notifications about Clash of Code games"
    bot.send_message(chat_id=update.message.chat_id,
            reply_to_message_id=message_id,
            text=msg)
    log_print('Clash of Code disable', username)

def clash_enable(config, bot, update):
    username = update.message.from_user.username
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    if not username:
        msg = "The unnamed ones are free from these silly humans vanity"
    else:
        with connector(config.engine()) as ses:
            all_excludes = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            all_excludes = [ x for x in all_excludes for x in x ]
            if username in all_excludes:
                ses.query(ClashExclude).filter(and_(
                    ClashExclude.chat_id == chat_id,
                    ClashExclude.username == username)).delete()
                msg = "You will be notified when a new game is created!"
            else:
                msg = "You've already subscribed"
    bot.send_message(chat_id=update.message.chat_id,
            reply_to_message_id=message_id,
            text=msg,
            parse_mode="markdown")
    log_print('Clash of Code enable', username)

def clash_results_usage(config, bot, update):

    message="""
    I haven't found the last game, try to use it like this:
    ```
    /clash_results GAME_ID
    ```
    """
    message = "\n".join([i.strip() for i in message.split('\n')])
    bot.send_message(chat_id=update.message.chat_id,
                     text=message,
                     parse_mode="markdown")

def clash_results(config, bot, update, args):

    clash_ids = []
    results = {}

    if args:
        clash_ids = (list(set(args)))
    else:
        try:
            with open("/tmp/clash_{}".format(update.message.chat_id), "r") as file:
                clash_ids = [json.loads(file.read())["clash_id"]]
        except IOError:
            pass

    if not clash_ids:
        clash_results_usage(config, bot, update)
        return

    for clash_id in clash_ids:
        r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/findClashReportInfoByHandle',
                          headers={"content-type":"application/json;charset=UTF-8"},
                          data='[{}]'.format(clash_id))
        if r.status_code == 200:
            results = json.loads(r.text)
            if results["success"]:
                leaderboard = []
                clash_mode = results["success"]["mode"].capitalize() if "mode" in results["success"] else "Unknown"
                message = '''
                Game id: {clash_id}
                Game mode: {clash_mode}
                Status: {clash_status}
                '''.format(
                    clash_id=clash_id,
                    clash_mode=clash_mode,
                    clash_status="Finished" if results["success"]["finished"] else "In progress")
                if clash_mode != "Unknown":
                    if clash_mode == "SHORTEST":
                        for player in results["success"]["players"]:
                            cache = []
                            cache.insert(0, player["rank"])
                            cache.insert(1, player["codingamerNickname"])
                            cache.insert(2, '{}%'.format(player["score"]))
                            cache.insert(3, str(datetime.timedelta(milliseconds=player["duration"])).split('.', 2)[0])
                            cache.insert(4, player["criterion"])
                            leaderboard.insert(player["rank"], cache)
                        message += '```\n'
                        message += tabulate(sorted(leaderboard), headers=["", "Username", "Score", "Time", "Characters"], tablefmt='fancy_grid')
                        message += '```'
                    else:
                        for player in results["success"]["players"]:
                            cache = []
                            cache.insert(0, player["rank"])
                            cache.insert(1, player["codingamerNickname"])
                            cache.insert(2, '{}%'.format(player["score"]))
                            cache.insert(3, str(datetime.timedelta(milliseconds=player["duration"])).split('.', 2)[0])
                            leaderboard.insert(player["rank"], cache)
                        message += tabulate(sorted(leaderboard), headers=["", "Username", "Score", "Time"], tablefmt='fancy_grid')

                message = "\n".join([i.strip() for i in message.split('\n')])

                img = Image.new('RGB', (600, 270), color = (100, 100, 100))
                d = ImageDraw.Draw(img)
                img_fraction = 0.80
                font = ImageFont.truetype('/usr/share/fonts/Monospace.ttf', 1)
                while font.getsize(message)[0] < img_fraction*image.size[0]:
                    fontsize += 1
                    font = ImageFont.truetype('/usr/share/fonts/Monospace.ttf', fontsize)
                print(image.size)
                d.text((10,10), message, font=font, fill=(240,240,240))
                fontsize -= 1
                img.save('/tmp/report.png')
                bot.sendPhoto(chat_id=update.message.chat_id,
                              photo=open('/tmp/report.png', 'rb'),
                              reply_to_message_id=update.message.message_id)

    log_print('Clash of Code results for {}'.format(", ".join(clash_ids)))
