#!/bin/python3.6
import json
import requests
import pytz 

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime

with open('.tokens') as tokens:
    data = json.load(tokens)

globals().update(data)
updater = Updater(token=bot_token)
dispatcher = updater.dispatcher

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello")

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="No command")

def weather(bot, update, args):

    city = ' '.join(args) if args else city = 'Ленинград'

    w_params = {        'q': city, 
                      'key': weather_token, 
                   'format': 'json', 
                     'date': 'today', 
                     'fx24': 'yes', 
                     'lang': 'ru'            }

    w_response = requests.get('https://api.worldweatheronline.com/premium/v1/weather.ashx', w_params).json()

    temp  = w_response["data"]["current_condition"][0]["temp_C"]
    value = w_response["data"]["current_condition"][0]["lang_ru"][0]["value"]
    city  = w_response["data"]["request"][0]["query"]
    time  = datetime.strptime(w_response["data"]["current_condition"][0]["observation_time"] + " 2017", '%I:%M %p %Y')
    time  = pytz.timezone('Europe/Moscow').fromutc(time)
    time  = "{:%H:%M}".format(time)
    
    bot.send_message(chat_id=update.message.chat_id, text = '['+time+']'+' +'+temp+" "+value+"\n"+city)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

weather_handler = CommandHandler('weather', weather, pass_args=True)
dispatcher.add_handler(weather_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
