from functools import partial


def _hug_text(text, formatter):
    return f'<{formatter}>{text}</{formatter}>'


italize = partial(_hug_text, formatter='i')
boldize = partial(_hug_text, formatter='b')
