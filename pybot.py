#!/usr/bin/env python3
import json
import requests
import pytz 

from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from tokens import *

#===========FUNCTIONS========================================================

def start(bot, update):

    start_text = '''
    This is my first bot on Python.
    You can see the code here https://github.com/Cuttlerat/bashbot
    by @Cuttlerat
    '''
    start_text = "\n".join([ i.strip() for i in start_text.split('\n') ])
    bot.send_message(chat_id=update.message.chat_id, text = start_text)

def unknown(bot, update):

    bot.send_message(chat_id=update.message.chat_id, text="No such command")

def get_emoji(emoji_code):

    emoji_code = str(emoji_code)
    print(emoji_code)

    if "113" in emoji_code:
        emoji_code = emoji_code.replace("113","☀️")

    if "116" in emoji_code:
        emoji_code = emoji_code.replace("116","🌥")

    if "119" in emoji_code:
        emoji_code = emoji_code.replace("119","🌥")

    if "122" in emoji_code:
        emoji_code = emoji_code.replace("122","☁️")

    if "200" in emoji_code:
        emoji_code = emoji_code.replace("200","🌩")

    for i in ["143","248","260"]:
        if i in emoji_code:
            emoji_code = emoji_code.replace(i,"🌫")

    for i in ["176","263","266","281","293","296","299","302","311","317","362"]:
        if i in emoji_code:
            emoji_code = emoji_code.replace(i,"🌧")

    for i in ["179","182","185","227","230","323","326","329","332","335","338","350","353","368","371","374","377"]:
        if i in emoji_code:
            emoji_code = emoji_code.replace(i,"🌨")

    for i in ["284","305","308","314","320","356","359","365"]:
        if i in emoji_code:
            emoji_code = emoji_code.replace(i,"🌧")

    for i in ["386","389","392","395"]:
        if i in emoji_code:
            emoji_code = emoji_code.replace(i,"⛈")

    return(emoji_code)

def weather(bot, update, args):

    city = ' '.join(args) if args else 'Ленинград'

    w_params = {        'q': city, 
                      'key': WEATHER_TOKEN, 
                   'format': 'json', 
                     'date': 'today', 
                     'fx24': 'yes', 
                     'lang': 'ru'            }

    w_response = requests.get('https://api.worldweatheronline.com/premium/v1/weather.ashx', w_params).json()

    now_temp  = w_response["data"]["current_condition"][0]["temp_C"]
    if now_temp[0] != '-': now_temp='+'+now_temp

    now_comment = w_response["data"]["current_condition"][0]["lang_ru"][0]["value"]
    now_city  = w_response["data"]["request"][0]["query"]

    now_time  = datetime.strptime(w_response["data"]["current_condition"][0]["observation_time"] + " 2017", '%I:%M %p %Y')
    now_time  = pytz.timezone('Europe/Moscow').fromutc(now_time)
    now_time  = "{:%H:%M}".format(now_time)
    now_emoji = get_emoji(w_response["data"]["current_condition"][0]["weatherCode"])

    weather = {}
    for j in range(2):
        for i in range(3):
            weather[j,"temp",i]    = w_response["data"]["weather"][j]["hourly"][2+(i*3)]["tempC"]
            if weather[j,"temp",i][0] != '-': weather[j,"temp",i]='+'+weather[j,"temp",i]
            weather[j,"emoji",i]   = get_emoji(w_response["data"]["weather"][j]["hourly"][2+(i*3)]["weatherCode"])
            weather[j,"comment",i] = w_response["data"]["weather"][j]["hourly"][2+(i*3)]["lang_ru"][0]["value"]
    
    message = ''.join("""
    *Now:* 
    *[{0}]:* {1} {2} {3}
    {4}

    *Today:*
    *Morning:* {5} {6} {7}
    *Noon:* {8} {9} {10}
    *Evening:* {11} {12} {13}

    *Tommorow:* 
    *Morning:* {14} {15} {16}
    *Noon:* {17} {18} {19}
    *Evening:* {20} {21} {22}
    """.format(now_time,
               now_emoji,
               now_temp,
               now_comment,
               now_city,
               *[ weather[i] for i in weather ] ))
   
    message = "\n".join([ k.strip() for k in message.split('\n') ])
    
    bot.send_message(chat_id=update.message.chat_id, parse_mode = "markdown", text = message )

    # LOG
    log_dict = {'timestamp': datetime.now().strftime("[%H:%M]"), 
                  'message': "Weather {0}".format(now_city), 
                 'username': update.message.from_user.username }
    print("{timestamp}: \"{message}\" by @{username}".format(**log_dict))

def ibash(bot, update, args):

    count = int(''.join(args)) if ''.join(args).isdigit() else 1
    if count > 5: count = 5

    for i in range(count):
        i_response = requests.get('http://ibash.org.ru/random.php').text
        soup = BeautifulSoup(i_response, "html.parser")
        
        quote_id = soup.find_all("div", class_="quote")[0].a.get_text()
        for br in soup.find_all("br"): 
            br.replace_with("\n")
        quote_text = soup.find("div", class_="quotbody").text
        bot.send_message(chat_id = update.message.chat_id, text = quote_id+"\n"+quote_text+"\n", disable_web_page_preview = 1)

    # LOG
    log_dict = {'timestamp': datetime.now().strftime("[%H:%M]"), 
                    'count': count, 
                 'username': update.message.from_user.username }
    print("{timestamp}: ibash {count} by @{username}".format(**log_dict))

def loglist(bot, update, args):

    #TODO Merge into one function with ibash
    #     I need help with getting a what command was in message inside function to do that
    count = int(''.join(args)) if ''.join(args).isdigit() else 1
    if count > 5: count = 5

    for i in range(count):
        l_raw_json = json.loads(requests.get('https://loglist.net/api/quote/random').text)
        quote_id   = l_raw_json['id']
        quote_text = l_raw_json['content']
        bot.send_message(chat_id = update.message.chat_id, text = "#"+quote_id+"\n"+quote_text+"\n", disable_web_page_preview = 1)

    # LOG
    log_dict = {'timestamp': datetime.now().strftime("[%H:%M]"), 
                    'count': count, 
                 'username': update.message.from_user.username }
    print("{timestamp}: loglist {count} by @{username}".format(**log_dict))



#============================================================================


updater    = Updater(token=BOT_TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('weather', weather, pass_args=True))
dispatcher.add_handler(CommandHandler('w', weather, pass_args=True))
dispatcher.add_handler(CommandHandler('ibash', ibash, pass_args=True))
dispatcher.add_handler(CommandHandler('loglist', loglist, pass_args=True))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater.start_polling()
