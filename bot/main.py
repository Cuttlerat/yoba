#!/usr/bin/env python3

# ===============================================================================
#
#    DESCRIPTION: Telegram bot in python
#         AUTHOR: Kioller Alexey
#         E-MAIL: avkioller@gmail.com
#         GITHUB: https://github.com/Cuttlerat/pybot
#        CREATED: 02.08.2017
#        VERSION: 1.0
#
# ===============================================================================

import logging
import sqlite3

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackQueryHandler
)

from config import Config
from handlers.crypto import crypto
from handlers.db import database_handler
from handlers.helpers import start, bug, chat_id
from handlers.parser import parser
from handlers.pinger import pinger
from handlers.weather import weather, wset
from logger import log_print
from models.models import create_table

if __name__ == '__main__':
    config = Config()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    db_handler = lambda bot, update, args: database_handler(config, bot, update, args)
    weather_handler = lambda bot, update, args: weather(config, bot, update, args)
    wset_handler = lambda bot, update, args: wset(config, bot, update, args)
    parser_handler = lambda bot, update: parser(config, bot, update)
    pinger_handler = lambda bot, update, args: pinger(config, bot, update, args)

    log_print('Started')

    try:
        create_table(config)

        updater = Updater(token=config.telegram_token())
        dispatcher = updater.dispatcher

        [dispatcher.add_handler(i) for i in [
            CommandHandler('bug', bug),
            CommandHandler('chatid', chat_id),
            CommandHandler(['start', 'info'], start),
            CommandHandler(['weather', 'w'], weather_handler, pass_args=True),
            CommandHandler('wset', wset_handler, pass_args=True),
            CommandHandler('db', db_handler, pass_args=True),
            CommandHandler('ping', pinger_handler, pass_args=True),
            CommandHandler('crypto', crypto, pass_args=True),
            MessageHandler(Filters.text, parser_handler)
        ]]

        if config.telegram_mode().lower() == 'webhook':
            updater.start_webhook(listen=config.listen_ip(),
                                  port=config.webhook_port(),
                                  url_path=config.telegram_token())
            updater.bot.set_webhook(config.webhook_url())
            updater.idle()
        else:
            updater.start_polling()
    except sqlite3.ProgrammingError:
        pass
