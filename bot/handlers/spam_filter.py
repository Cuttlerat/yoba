from logger import log_print
from models.models import connector, Spam
from sqlalchemy import and_
import datetime
import redis

def spam_check(config, bot, update, args):

    chat_id = update.message.chat_id
    with connector(config.engine()) as ses:
        spamers = ses.query(Spam.username, Spam.requests).filter(Spam.chat_id == update.message.chat_id).distinct().all()
        for spamer in spamers:
            username, requests = spamer
            redis_db = config.redis
            try:
                redis_key = "{username}_{chat_id}_{date}".format(
                    username=username,
                    chat_id=chat_id,
                    date=datetime.datetime.now().strftime("%Y-%m-%d"))
                current = redis_db.get(redis_key)
                print(current)
                redis_db.set(redis_key, requests)
            except redis.RedisError:
                print("Fail")
