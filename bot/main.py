#!/usr/bin/env python3

# ===============================================================================
#
#    DESCRIPTION: Telegram bot in python
#         AUTHOR: Kioller Alexey
#         E-MAIL: avkioller@gmail.com
#         GITHUB: https://github.com/Cuttlerat/yoba
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
from handlers.clash import clash, clash_start, clash_disable, clash_enable, clash_results
from handlers.db import database_handler
from handlers.helpers import start, bug, chat_id
from handlers.parser import parser
from handlers.pinger import Pinger
from handlers.me import me
from logger import log_print
from models.models import create_table


def handler(action, input_config):
    def new_action(bot, update, **kwargs):
        action(input_config, bot, update, **kwargs)

    return new_action

def main():
    config = Config()
    register(config)

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    tglogger = logging.getLogger("telegram.bot")
    tglogger.setLevel(logging.ERROR)

    pinger = Pinger()


    functions = [database_handler,
                 me,
                 parser,
                 clash,
                 clash_start,
                 clash_enable,
                 clash_disable,
                 clash_results]

    db_handler,\
    me_handler,\
    parser_handler,\
    clash_handler,\
    clash_start_handler,\
    clash_enable_handler,\
    clash_disable_handler,\
    clash_results_handler = (handler(act, config) for act in functions)

    log_print('Started', level="INFO", command="main")

    try:
        create_table(config)

        updater = Updater(token=config.telegram_token())
        dispatcher = updater.dispatcher

        [dispatcher.add_handler(i) for i in [
            CommandHandler(['bug', 'issue'], bug),
            CommandHandler('chatid', chat_id),
            CommandHandler(['start', 'info'], start),
            CommandHandler('me', me_handler, pass_args=True),
            CommandHandler('db', db_handler, pass_args=True),
            CommandHandler('ping_add_me', pinger.add_me, pass_args=True),
            CommandHandler('ping_show', pinger.show, pass_args=True),
            CommandHandler('ping_show_me', pinger.show_me, pass_args=True),
            CommandHandler('ping_show_all', pinger.show_all),
            CommandHandler('ping_delete', pinger.delete, pass_args=True),
            CommandHandler('ping_drop', pinger.drop, pass_args=True),
            CommandHandler('ping_add', pinger.add, pass_args=True),
            CommandHandler('clash', clash_handler),
            CommandHandler('clash_start', clash_start_handler),
            CommandHandler('clash_enable', clash_enable_handler),
            CommandHandler('clash_disable', clash_disable_handler),
            CommandHandler('clash_results', clash_results_handler, pass_args=True),
            MessageHandler(Filters.all, parser_handler)
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

if __name__ == '__main__':
    main()
