#!/bin/python3.6
import json
import requests
import pytz 

from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime

#===========VARIABLES========================================================

with open('.tokens') as tokens:
    data = json.load(tokens)

globals().update(data)

#===========FUNCTIONS========================================================

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello")

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="No command")

def weather(bot, update, args):

    city = ' '.join(args) if args else 'Ленинград'

    w_params = {        'q': city, 
                      'key': weather_token, 
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

    #TODO Make a log function
    log_dict = {'timestamp': datetime.now().strftime("[%H:%M]"), 
                    'count': count, 
                 'username': update.message.from_user.username }
    print("{timestamp}: ibash {count} by @{username}".format(**log_dict))

#============================================================================


updater    = Updater(token=bot_token)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('weather', weather, pass_args=True))
dispatcher.add_handler(CommandHandler('w', weather, pass_args=True))
dispatcher.add_handler(CommandHandler('ibash', ibash, pass_args=True))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

updater.start_polling()
