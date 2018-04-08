import pyowm
import pytest
from pyowm.exceptions.unauthorized_error import UnauthorizedError


class TestWeather:
    def test_smoke_weather_api(self, config):
        token = config.weather_token()
        owm = pyowm.OWM(token, language='en')
        owm.weather_at_place("Moscow")

    def test_wrong_token(self):
        token = "abyrabyrvalg"
        with pytest.raises(UnauthorizedError):
            owm = pyowm.OWM(token, language='en')
            owm.weather_at_place("Moscow")
