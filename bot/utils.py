from functools import partial


def _hug_text(text, formatter):
    return f'<{formatter}>{text}</{formatter}>'


italize = partial(_hug_text, formatter='i')
boldize = partial(_hug_text, formatter='b')

def send_typing_action(bot, update):
    bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
