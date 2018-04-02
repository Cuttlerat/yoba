import requests


class CoinRate:
    URL_STRING = "https://api.cryptonator.com/api/ticker/"

    @staticmethod
    def get_rate(cur: str, cash: str) -> str:
        try:
            request = requests.get(CoinRate.URL_STRING + cur + "-" + cash)
            response = request.json()
            rate = round(float(response['ticker']['price']), 2)
        except KeyError:
            rate = 'None'
        return str(rate)
