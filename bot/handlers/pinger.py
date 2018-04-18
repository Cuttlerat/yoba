from odr.injector import inject
from sqlalchemy import and_

from config import Config
from logger import log_print
from models.models import connector, Pingers


class Pinger:
    @inject
    def __init__(self, config: Config):
        self.config = config

    def show(self, bot, update, args):
        usernames = " ".join(args).split()
        username = usernames[0] if usernames else ""
        if not username:
            username = update.message.from_user.username
        elif username[0] == "@":
            username = username[1:]
        else:
            usage_text = "Usage:\n`/ping_show @username`\n`/ping_show me`\n`/ping_show`\n"
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode='markdown',
                             text=usage_text)
            return

        with connector(self.config.engine()) as ses:
            user_matches = ses.query(Pingers).filter(Pingers.chat_id == update.message.chat_id,
                                                     Pingers.username == username).all()
            out_text = ""
            for match in user_matches:
                out_text += "\n{}".format(match.match)
            if out_text == "":
                out_text = "No such user"
            bot.send_message(chat_id=update.message.chat_id,
                             text=out_text)
            log_print('Show pings of "@{0}", by {1}'.format(username, update.message.from_user.username))

    def show_all(self, bot, update):
        if update.message.from_user.username not in self.config.admins():
            message = "This command is only allowed for admins."
            bot.send_message(chat_id=update.message.chat_id,
                             text=message)
            return

        with connector(self.config.engine()) as ses:
            all_matches = ses.query(Pingers).filter(Pingers.chat_id == update.message.chat_id).all()
            out_text = ""
            for match in all_matches:
                out_text += "\n{0} | {1}".format(match.username, match.match)
            bot.send_message(chat_id=update.message.chat_id,
                             text=out_text)

    def delete(self, bot, update, args):
        usernames = [name[1:] for name in args if name[0] == "@"]
        matches = [match for match in args if match[0] != "@"]

        user = update.message.from_user.username
        if not usernames:
            usernames = [user]

        if not matches:
            usage_text = "Usage:\n`/ping_delete [@username] [match]`\n`/ping_delete [match]`"
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode='markdown',
                             text=usage_text)
            return

        if user not in self.config.admins() and (len(usernames) > 1 or len(
                list(filter(lambda x: x != user, usernames))) != 0):
            message = "Deleting pings of another users is only allowed for admins."
            bot.send_message(chat_id=update.message.chat_id,
                             text=message)
            return

        answer = ""
        with connector(self.config.engine()) as ses:
            for username in usernames:
                for match in matches:
                    result = ses.query(Pingers).filter(and_(
                        Pingers.chat_id == update.message.chat_id,
                        Pingers.username == username,
                        Pingers.match == match))
                    if not result.all():
                        answer += "Match `{0}` for user `@{1}` not found\n".format(match, username)
                    else:
                        result.delete()
                        answer += "Match `{0}` for user `@{1}` deleted\n".format(match, username)
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode='markdown',
                         text=answer)

    def drop(self, bot, update, args):
        if update.message.from_user.username not in self.config.admins():
            message = "This command is only allowed for admins."
            bot.send_message(chat_id=update.message.chat_id,
                             text=message)
            return
        usernames = [name[1:] for name in args if name[0] == "@"]

        if not usernames:
            usage_text = "Usage: `/ping_drop [@username]`\n"
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode='markdown',
                             text=usage_text)
            return

        answer = ""
        with connector(self.config.engine()) as ses:
            for username in usernames:
                result = ses.query(Pingers).filter(and_(
                    Pingers.chat_id == update.message.chat_id,
                    Pingers.username == username))
                if not result.all():
                    answer += "User `@{0}` not found\n".format(username)
                else:
                    result.delete()
                    answer += "User `@{0}` deleted\n".format(username)
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode='markdown',
                         text=answer)

    def add(self, bot, update, args):
        usernames = [name[1:] for name in args if name[0] == "@"]
        matches = [match for match in args if match[0] != "@"]

        user = update.message.from_user.username
        if not usernames:
            usernames = [user]

        if not matches:
            usage_text = "Usage:\n`/ping_add [@username] [match]`\n`/ping_add [match]`"
            bot.send_message(chat_id=update.message.chat_id,
                             parse_mode='markdown',
                             text=usage_text)
            return

        if user not in self.config.admins() and (len(usernames) > 1 or len(
                list(filter(lambda x: x != user, usernames))) != 0):
            message = "Adding pings for another users is only allowed for admins."
            bot.send_message(chat_id=update.message.chat_id,
                             text=message)
            return

        if user not in self.config.admins():
            with connector(self.config.engine()) as ses:
                count = ses.query(Pingers).filter(and_(
                    Pingers.chat_id == update.message.chat_id,
                    Pingers.username == user)).count()
            if count + len(matches) > 10:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="You can add only 10 matches")
                log_print('Pinger limit is exhausted', user)
                return

        answer = ""
        with connector(self.config.engine()) as ses:
            for username in usernames:
                for match in matches:
                    ping = Pingers(
                        username=username,
                        match=match,
                        chat_id=update.message.chat_id)
                    ses.add(ping)
                    answer += "Match `{0}` for user `@{1}` has been added\n".format(match, username)
        bot.send_message(chat_id=update.message.chat_id,
                         parse_mode='markdown',
                         text=answer)
