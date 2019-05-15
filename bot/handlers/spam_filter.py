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
                current_req = int(redis_db.get(redis_key))
                print(current_req)
                if current_req is not None:
                    if current_req > 0:
                        redis_db.decr(redis_key)
                        print("Decreased")
                    else:
                        print("Banned", username, current_req)
                else:
                    redis_db.set(redis_key, requests)

                print(username, current_req)
            except redis.RedisError:
                print("Fail")
