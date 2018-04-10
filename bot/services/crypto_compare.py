import requests


class CryptoCompare:
    URL_STRING = "https://min-api.cryptocompare.com/"

    @staticmethod
    def get_rate(crypto=None, currencies=None):
        if currencies is None:
            currencies = ['USD']
        if crypto is None:
            crypto = ['BTC']
        final_url = CryptoCompare.URL_STRING + "data/pricemulti?" + "fsyms=" + ",".join(crypto) + "&tsyms=" + ",".join(
            currencies)
        request = requests.get(final_url)
        response = request.json()
        return response
