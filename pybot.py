#!/bin/python3.6
import json
import logging
import urllib
import requests

from urllib.parse import urlparse
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

with open('.tokens') as tokens:
    data = json.load(tokens)

globals().update(data)

updater = Updater(token=bot_token)
dispatcher = updater.dispatcher
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello")

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="No command")

def weather(bot, update):

    w_params = {        'q': 'Ленинград', 
                      'key': weather_token, 
                   'format': 'json', 
                     'date': 'today', 
                     'fx24': 'yes', 
                     'lang': 'ru'            }

    w_response = requests.get('https://api.worldweatheronline.com/premium/v1/weather.ashx', w_params).json()

    temp=w_response["data"]["current_condition"][0]["temp_C"]
    value= w_response["data"]["current_condition"][0]["lang_ru"][0]["value"]
    bot.send_message(chat_id=update.message.chat_id, text= '+'+temp+" "+value)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

weather_handler = CommandHandler('weather', weather)
dispatcher.add_handler(weather_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.start_polling()
