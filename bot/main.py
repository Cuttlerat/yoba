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
from handlers.db import database_handler
from handlers.helpers import start, bug, hat, chat_id, buttons
from handlers.parser import parser
from handlers.pinger import pinger_handler
from handlers.random_content import random_content
from handlers.weather import weather, wset
from logger import log_print
from models.models import create_table

if __name__ == '__main__':
    config = Config()

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    log_print('Started')

    try:
        create_table()

        updater = Updater(token=config.telegram_token())
        dispatcher = updater.dispatcher

        [dispatcher.add_handler(i) for i in [
            CommandHandler('bug', bug),
            CommandHandler('chatid', chat_id),
            CommandHandler(['start', 'info'], start),
            CommandHandler(['weather', 'w'], weather, pass_args=True),
            CommandHandler('hat', hat),
            CommandHandler(
                ['ibash', 'loglist', 'cat', 'dog'],
                random_content, pass_args=True
            ),
            CommandHandler('wset', wset, pass_args=True),
            CommandHandler('db', database_handler, pass_args=True),
            CommandHandler('ping', pinger_handler, pass_args=True),
            CallbackQueryHandler(buttons),
            MessageHandler(Filters.text, parser)
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
