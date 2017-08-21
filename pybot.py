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

def weather(bot, update, args):

    city = ' '.join(args) if args else 'Ленинград'

    w_params = {        'q': city, 
                      'key': WEATHER_TOKEN, 
                   'format': 'json', 
                     'date': 'today', 
                     'fx24': 'yes', 
                     'lang': 'ru'            }

    w_response = requests.get('https://api.worldweatheronline.com/premium/v1/weather.ashx', w_params).json()

    temp  = w_response["data"]["current_condition"][0]["temp_C"]
    if temp[0] != '-': temp='+'+temp

    value = w_response["data"]["current_condition"][0]["lang_ru"][0]["value"]
    city  = w_response["data"]["request"][0]["query"]

    time  = datetime.strptime(w_response["data"]["current_condition"][0]["observation_time"] + " 2017", '%I:%M %p %Y')
    time  = pytz.timezone('Europe/Moscow').fromutc(time)
    time  = "{:%H:%M}".format(time)
    
    message = ''.join("[{0}]: {1} {2}\n{3}".format(time,temp,value,city))
    bot.send_message(chat_id=update.message.chat_id, text = message )

    # LOG
    log_dict = {'timestamp': datetime.now().strftime("[%H:%M]"), 
                  'message': message.replace('\n', ' '), 
                 'username': update.message.from_user.username }
    print("{timestamp}: \"{message}\" by @{username}".format(**log_dict))

def ibash(bot, update, args):

    #TODO NaN check
    count = int(''.join(args)) if args else 1
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
    count = int(''.join(args)) if args else 1
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
