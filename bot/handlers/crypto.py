from services.coint_rate import CoinRate


def crypto(bot, update, args):
    error = ''
    try:
        if args[0] in ["rub", "rur"]:
            cash = "rur"
            cash_symbol = "₽"
        elif args[0] in ["usd"]:
            cash = "usd"
            cash_symbol = "$"
        else:
            raise NotImplementedError("Only USD and RUR currencies now supported")
    except NotImplementedError as e:
        error = str(e)
        cash = "usd"
        cash_symbol = "$"
    except Exception as e:
        cash = "usd"
        cash_symbol = "$"
    prices = {}
    for i in ["btc", "bch", "eth", "xmr"]:
        prices[i] = CoinRate.get_rate(cur=i, cash=cash)

    message = "```\n"
    if error != '':
        message += "Warning: {}\n".format(error)
    for price in prices:
        if prices[price] == 'None':
            message += "No information about {}\n".format(price.upper())
        else:
            message += "1 {0} = {2}{1}\n".format(price.upper(), prices[price], cash_symbol)
    message += "```"
    bot.send_message(chat_id=update.message.chat_id,
                     text=message,
                     parse_mode="markdown")
