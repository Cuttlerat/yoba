from config import Config
from logger import log_print


def mute_on(config, bot, update):
    username = update.message.from_user.username
    if username not in config.admins():
        message = "Mute commands only for admins"
        bot.send_message(chat_id=update.message.chat_id,
                         text=message)
        return

    if config.get_mute():
        message = "Global silence already activated."
    else:
        config.set_mute(True)
        message = "Global silence activated."
        log_print('Mute on', username)
    bot.send_message(chat_id=update.message.chat_id,
                     text=message)


def mute_off(config, bot, update):
    username = update.message.from_user.username
    if username not in config.admins():
        message = "Mute commands only for admins"
        bot.send_message(chat_id=update.message.chat_id,
                         text=message)
        return

    if config.get_mute(): 
        config.set_mute(False)
        message = "Global silence deactivated."
        log_print('Mute off', username)
    else:
        message = "Global silence is not activated."
        
    bot.send_message(chat_id=update.message.chat_id,
                     text=message)

def mute(config, bot, update):
    
    chat_id=update.message.chat_id
    user_id=update.message.from_user.id
    if config.get_mute():
        try:
            bot.restrict_chat_member(chat_id, user_id, until_date=time()+300)
        except BadRequest:
            return
        bot.send_message(chat_id, text="Muted for 5 minutes",
                     reply_to_message_id=update.message.message_id)
