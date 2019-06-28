from logger import log_print
import requests
import json
from models.models import connector, ClashExclude, Pingers
from sqlalchemy import and_
import datetime
from tabulate import tabulate
from PIL import Image, ImageDraw, ImageFont
import io
import redis
import os
import telegram
from utils import send_typing_action, send_uploading_photo_action

class NotLoggedException(Exception):
    pass

def clash_get_cookies(config):
    cookies = {}
    redis_db = config.redis
    if redis_db and redis_db.exists("clash_cookies"):
        cookies = json.loads(redis_db.get("clash_cookies"))
    else:
        r = requests.post('https://www.codingame.com/services/CodingamerRemoteService/loginSiteV2',
                          headers={"content-type":"application/json;charset=UTF-8",
                                   "user-agent": ""},
                          data='[{user}, {password}, true]'.format(
                              user=config.clash_login,
                              password=config.clash_password))
        if r.status_code == 200:
            cookies = {**r.cookies.get_dict(),
                    "user_id": json.loads(r.text)["success"]["user"]["id"]}
            try:
                tomorrow = datetime.datetime.now() + datetime.timedelta(1)
                midnight = datetime.datetime(year=tomorrow.year,
                                             month=tomorrow.month,
                                             day=tomorrow.day,
                                             hour=0,
                                             minute=0,
                                             second=0)
                redis_db.set("clash_cookies", json.dumps(cookies))
                redis_db.expireat("clash_cookies", midnight)
            except redis.RedisError as e:
                log_print("Could not save Clash cookies in redis",
                          error=str(e),
                          level="WARN",
                          command="clash")

    if "user_id" and "rememberMe" and "cgSession" in cookies:
        return cookies
    else:
        log_print("Could not get cookies from codingame.com",
                  level="ERROR",
                  command="clash")
        raise NotLoggedException(r)

def clash(config, bot, update):
    send_typing_action(bot, update)

    last_game={}
    username = update.message.from_user.username
    last_game = get_last_game(config, username, update.message.chat_id)
    clash_id = ""
    users = ""
    cookies = clash_get_cookies(config)

    if last_game["clash_id"]:

        r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/findClashReportInfoByHandle',
                          headers={"content-type":"application/json;charset=UTF-8"},
                          data='[{}]'.format(last_game["clash_id"]))
        if r.status_code == 200:
            results = json.loads(r.text)
            if results["success"]["started"] or results["success"]["finished"]:
                r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/createPrivateClash',
                    headers={"content-type":"application/json;charset=UTF-8",
                             "cookie":"rememberMe={remember_me};cgSession={cg_session}".format(
                                 remember_me=cookies["rememberMe"],
                                 cg_session=cookies["cgSession"])},
                    data='[{user_id}, {{"SHORT":true}}]'.format(user_id=cookies["user_id"]))
                if r.status_code == 200:
                    clash_id = json.loads(r.text)["success"]["publicHandle"]
            else:
                try:
                    bot.delete_message(chat_id=update.message.chat_id,
                                       message_id=last_game["message_id"])
                except telegram.error.BadRequest:
                    pass
                clash_id = last_game["clash_id"]
    else:
        r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/createPrivateClash',
                          headers={"content-type":"application/json;charset=UTF-8",
                                   "cookie":"rememberMe={remember_me};cgSession={cg_session}".format(
                                       remember_me=cookies["rememberMe"],
                                       cg_session=cookies["cgSession"])},
                          data='[{user_id}, {{"SHORT":true}}]'.format(user_id=cookies["user_id"]))
        if r.status_code == 200:
            clash_id = json.loads(r.text)["success"]["publicHandle"]

    if clash_id:
        with connector(config.engine()) as ses:
            all_matches = ses.query(Pingers.username).filter(Pingers.chat_id == update.message.chat_id).order_by(Pingers.username).distinct().all()
            exclude = ses.query(ClashExclude.username).filter(ClashExclude.chat_id == update.message.chat_id).all()
            users = [ x for x in all_matches if x not in exclude ]
            users = [ x for x in users for x in x ]
            out_text = ""
        users=" ".join(["@{}".format(user) for user in users])
        message = """
Clash of Code!

https://www.codingame.com/clashofcode/clash/{clash_id}

{users}

Please send /clash_disable if you don't want to receive these notifications
        """.format(clash_id=clash_id, users=users)
        if "clash_id" in last_game and last_game["clash_id"] != clash_id:
            last_game["username"] = username
        last_game["clash_id"] = clash_id
        log_print("Created",
                  chat_id=update.message.chat_id,
                  username=username,
                  clash_id=clash_id,
                  level="INFO",
                  command="clash")
    else:
        log_print("Failed on creating",
                  chat_id=update.message.chat_id,
                  username=username,
                  clash_id=clash_id,
                  level="ERROR",
                  command="clash")
        message = "Something went wrong..."

    sent = bot.send_message(chat_id=update.message.chat_id,
                     text=message)
    last_game["users"] = users
    last_game["message_id"] = sent.message_id

    save_last_game(config, last_game, update.message.chat_id)


def save_last_game(config, last_game, chat_id):
    redis_db = config.redis
    saved_to_redis = False
    if redis_db:
        try:
            redis_db.set("clash_{}".format(chat_id), json.dumps(last_game))
            log_print("Saved to redis",
                      last_game=last_game,
                      key="clash_{}".format(chat_id),
                      level="DEBUG",
                      func="save_last_game")
            saved_to_redis = True
        except redis.RedisError as e:
            log_print("Could not save last_game to redis",
                      error=str(e),
                      level="WARN",
                      command="clash")

    if not saved_to_redis:
        try:
            with open("/tmp/clash_{}".format(chat_id), "w") as file:
                file.write(json.dumps(last_game))
        except IOError as io_e:
            log_print("Could not save last_game to file",
                      error=str(io_e),
                      level="CRITICAL",
                      func="save_last_game")
            raise

def get_last_game(config, username, chat_id):

    redis_db = config.redis
    got_from_redis = False
    delete_file_after_read = False

    if redis_db:
        try:
            last_game = redis_db.get("clash_{}".format(chat_id))
            if last_game:
                last_game = json.loads(last_game)
                got_from_redis = True
            else:
                got_from_redis = False
            log_print("Read from redis",
                      last_game=last_game,
                      key="clash_{}".format(chat_id),
                      level="DEBUG",
                      func="get_last_game")
        except redis.RedisError as e:
            log_print("Could not read last_game from redis",
                      error=str(e),
                      level="WARN",
                      command="clash")

    if not got_from_redis:
        if os.path.isfile("/tmp/clash_{}".format(chat_id)):
            last_game = get_last_game_from_file(config, username, chat_id)
            os.remove("/tmp/clash_{}".format(chat_id))
            save_last_game(config, last_game, chat_id)
        else:
            last_game = {"clash_id":"",
                         "message_id":"",
                         "users": "",
                         "username": username}

    return last_game

def get_last_game_from_file(config, username, chat_id):

    last_game = {"clash_id":"", "message_id":"", "users": "", "username": username}
    try:
        with open("/tmp/clash_{}".format(chat_id), "r") as file:
            last_game = json.loads(file.read())
    except IOError as io_e:
        log_print("Could not read last_game from file",
                  error=str(io_e),
                  level="WARN",
                  func="get_last_game")
    return last_game

def clash_start(config, bot, update):
    send_typing_action(bot, update)

    username = update.message.from_user.username

    last_game = get_last_game(config, username, update.message.chat_id)
    cookies = clash_get_cookies(config)

    if last_game["clash_id"]:
        if last_game["username"] == username:
            r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/startClashByHandle',
                headers={"content-type":"application/json;charset=UTF-8",
                         "cookie":"rememberMe={remember_me};cgSession={cg_session}".format(
                             remember_me=cookies["rememberMe"],
                             cg_session=cookies["cgSession"])},
                data='[{user_id}, "{clash_id}"]'.format(user_id=cookies["user_id"],
                    clash_id=last_game["clash_id"]))

            if r.status_code == 200 and "error" not in json.loads(r.text):
                message="The game is about to start, hurry up!"
                if last_game["users"]:
                    message = '{users}\n\n{msg}'.format(
                        users=last_game["users"],
                        msg=message)
                log_print("Started",
                          chat_id=update.message.chat_id,
                          username=username,
                          clash_id=last_game["clash_id"],
                          level="INFO",
                          command="clash_start")
            else:
                message = 'Could not start "{}" Clash game...'.format(
                    last_game["clash_id"])
                log_print("Failed on start",
                          chat_id=update.message.chat_id,
                          username=username,
                          clash_id=last_game["clash_id"],
                          level="ERROR",
                          command="clash_start")
        else:
            last_game["message_id"] = update.message.message_id
            message = 'Only @{} is allowed to start the game'.format(last_game["username"])
    else:
        last_game["clash_id"] = "None"
        message = "Could not find the last Clash id"

    if last_game["message_id"]:
        bot.send_message(chat_id=update.message.chat_id,
                         reply_to_message_id=last_game["message_id"],
                         text=message)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text=message)


def clash_disable(config, bot, update):
    send_typing_action(bot, update)

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
    log_print("Disabled",
              chat_id=update.message.chat_id,
              username=username,
              level="INFO",
              command="clash_disable")

def clash_enable(config, bot, update):
    send_typing_action(bot, update)
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
    log_print("Enabled",
              chat_id=update.message.chat_id,
              username=username,
              level="INFO",
              command="clash_disable")

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

def clash_results_to_byte_arr(message):

    font = ImageFont.truetype('/usr/share/fonts/Monospace.ttf', 48)
    img = Image.new('RGB', (100, 100), color = (50, 50, 50))
    d_temp = ImageDraw.Draw(img)
    text_size = d_temp.textsize(message, font)
    start_pos = (50, 20)
    text_size = (text_size[0]+start_pos[0]*2, text_size[1]+start_pos[1]*2)
    img = img.resize(text_size)
    d = ImageDraw.Draw(img)
    d.text(start_pos, message, font=font, fill=(240,240,240))

    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

def clash_results(config, bot, update, args):
    send_uploading_photo_action(bot, update)

    username = update.message.from_user.username
    clash_ids = []
    results = {}

    if args:
        clash_ids = (list(set(args)))
    else:
        last_id = get_last_game(config, username, update.message.chat_id)["clash_id"]
        if last_id:
            clash_ids = [last_id]

    if not clash_ids:
        clash_results_usage(config, bot, update)
        return

    for clash_id in clash_ids:
        r = requests.post('https://www.codingame.com/services/ClashOfCodeRemoteService/findClashReportInfoByHandle',
                          headers={"content-type":"application/json;charset=UTF-8"},
                          data='[{}]'.format(clash_id))
        if r.status_code == 200:
            results = json.loads(r.text)
            if "success" in results and results["success"]:
                leaderboard = []
                clash_mode = results["success"]["mode"].capitalize() if "mode" in results["success"] else "Unknown"
                message = '''
                Game id: {clash_id}
                Game mode: {clash_mode}
                Status: {clash_status}
                Creation time: {clash_creation_time}

                '''.format(
                    clash_id=clash_id,
                    clash_mode=clash_mode,
                    clash_creation_time=results["success"]["creationTime"],
                    clash_status="Finished" if results["success"]["finished"] else "In progress")
                if clash_mode != "Unknown":
                    headers=["", "Username", "Language", "Score", "Time"]
                    if clash_mode == "Shortest":
                        headers.append("Characters")
                    for player in results["success"]["players"]:
                        cache = []
                        cache.insert(0, player["rank"] if "rank" in player else 0)
                        cache.insert(1, player["codingamerNickname"] if "codingamerNickname" in player else "Unknown")
                        cache.insert(2, player["languageId"] if "languageId" in player else "Unknown")
                        cache.insert(3, '{}%'.format(player["score"] if "score" in player else "0"))
                        cache.insert(4, str(datetime.timedelta(milliseconds=player["duration"] if "duration" in player else 0)).split('.', 2)[0])
                        if clash_mode == "Shortest":
                            cache.insert(5, player["criterion"] if "criterion" in player else 0)

                        leaderboard.insert(player["rank"] if "rank" in player else 0, cache)

                    message += tabulate(sorted(leaderboard),
                                        headers,
                                        tablefmt='psql')
                message += "\n"
                message = "\n".join([i.strip() for i in message.split('\n')])

                img_byte_arr = clash_results_to_byte_arr(message)

                bot.sendPhoto(chat_id=update.message.chat_id,
                              photo=io.BufferedReader(img_byte_arr),
                              caption='https://www.codingame.com/clashofcode/clash/report/{}'.format(
                                       clash_id))

    log_print("Results",
              chat_id=update.message.chat_id,
              username=username,
              clash_id=clash_id,
              level="INFO",
              command="clash_results")
