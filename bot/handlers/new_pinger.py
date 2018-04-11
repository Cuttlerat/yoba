from config import Config
from logger import log_print
from models.models import connector, Pingers


class Pinger:
    def __init__(self, config: Config):
        self.config = config

    def show(self, bot, update, args):
        usernames = " ".join(args).split()
        username = usernames[0] if usernames else ""
        if not username or username == "me":
            username = update.message.from_user.username
        elif username[0] == "@":
            username = username[1:]
        else:
            usage_text = "Usage: \n`/ping_show @username`\n`/ping_show me`\n`/ping_show`\n"
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
            log_print('Show pings of "{0}", by {1}'.format(username, update.message.from_user.username))

    def show_all(self, bot, update):
        if update.message.from_user.username not in self.config.admins():
            message = "This command is allowed only for admins. This incident will be reported."
            bot.send_message(chat_id=update.message.chat_id,
                             text=message)
            return

        with connector(self.config.engine()) as ses:
            all_matches = ses.query(Pingers).filter(Pingers.chat_id == update.message.chat_id).all()
            out_text = ""
            for match in all_matches:
                out_text += "\n@{0} | {1}".format(match.username, match.match)
            bot.send_message(chat_id=update.message.chat_id,
                             text=out_text)
