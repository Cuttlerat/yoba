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

from odr.container import register
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters
)

from config import Config
from handlers.crypto import crypto
from handlers.coc import coc, coc_start, coc_disable, coc_enable
from handlers.db import database_handler
from handlers.helpers import start, bug, chat_id
from handlers.parser import parser
from handlers.muter import mute, mute_on, mute_off
from handlers.pinger import Pinger
from handlers.weather import weather, wset
from handlers.me import me
from logger import log_print
from models.models import create_table


def handler(action, input_config):
    def new_action(bot, update, **kwargs):
        action(input_config, bot, update, **kwargs)

    return new_action


if __name__ == '__main__':
    config = Config()
    register(config)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    pinger = Pinger()

    functions = [database_handler, weather, me, wset, parser, mute, mute_on, mute_off, coc, coc_start, coc_enable, coc_disable]
    db_handler, weather_handler, me_handler, wset_handler, parser_handler, mute_handler, mute_on_handler, mute_off_handler, coc_handler, coc_start_handler, coc_enable_handler, coc_disable_handler= \
        (handler(act, config) for act in functions)

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
            CommandHandler('me', me_handler, pass_args=True),
            CommandHandler('db', db_handler, pass_args=True),
            CommandHandler('ping_add_me', pinger.add_me, pass_args=True),
            CommandHandler('ping_show', pinger.show, pass_args=True),
            CommandHandler('ping_show_me', pinger.show_me, pass_args=True),
            CommandHandler('ping_show_all', pinger.show_all),
            CommandHandler('ping_delete', pinger.delete, pass_args=True),
            CommandHandler('ping_drop', pinger.drop, pass_args=True),
            CommandHandler('ping_add', pinger.add, pass_args=True),
            CommandHandler('mute_on', mute_on_handler),
            CommandHandler('mute_off', mute_off_handler),
            CommandHandler('crypto', crypto),
            CommandHandler('coc', coc_handler),
            CommandHandler('coc_start', coc_start_handler),
            CommandHandler('coc_enable', coc_enable_handler),
            CommandHandler('coc_disable', coc_disable_handler),
            MessageHandler(Filters.all, mute_handler)
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
