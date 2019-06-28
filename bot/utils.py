from functools import partial, wraps


def _hug_text(text, formatter):
    return f'<{formatter}>{text}</{formatter}>'


italize = partial(_hug_text, formatter='i')
boldize = partial(_hug_text, formatter='b')

def send_typing_action(func):

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(update, context,  *args, **kwargs)
    return command_func
