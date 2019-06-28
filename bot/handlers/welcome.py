import asyncio

from sqlalchemy import literal, and_, or_
from sqlalchemy.orm.exc import NoResultFound

from telegram.error import BadRequest
from logger import log_print
from models.models import connector, Welcome
from utils import send_typing_action


@send_typing_action
def welcome(config, bot, update):

    with connector(config.engine()) as ses:
        try:
            input_message = ses.query(Welcome.welcome).all()
        except NoResultFound:
            return

    welcome_message = "Welcome @{}!".format(update.message.new_chat_members[0].username)
    for line in input_message:
        welcome_message += "\n{}".format("".join(line))

    log_print('Welcome "@{0}", added by @{1}'.format(update.message.new_chat_members[0].username,
                                                    update.message.from_user.username))
    bot.send_message(chat_id=update.message.chat_id,
                     text=welcome_message)

