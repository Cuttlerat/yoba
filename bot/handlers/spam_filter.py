from logger import log_print
from models.models import connector, Spam
from sqlalchemy import and_
import datetime
import redis

def spam_check(config, bot, update, args):

    with connector(config.engine()) as ses:
        spamers = ses.query(Spam.username, Spam.requests).filter(Spam.chat_id == update.message.chat_id).distinct().all()
        for spamer in spamers:
            username, requests = spamer
            print(username, requests)
