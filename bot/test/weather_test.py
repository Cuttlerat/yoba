import pyowm
import pytest
from pyowm.exceptions.unauthorized_error import UnauthorizedError

from handlers.weather import weather


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

    def test_real_city(self, config, bot, update):
        city = 'Moscow'

        weather(config, bot, update, [city])

        assert city in bot.get_message()

    def test_fake_city(self, config, bot, update):
        city = "FakeCity_13"
        expected_answer = "The searched item was not found."

        weather(config, bot, update, [city])

        assert expected_answer in bot.get_message()

    def test_default_city_for_user(self, config, bot, update):
        expected_answer = "London"

        weather(config, bot, update, [])

        assert expected_answer in bot.get_message()

    def test_default_city_for_all(self, config, bot, update):
        expected_answer = "Syktyvkar"
        update.set_message(message="", username="test_two")

        weather(config, bot, update, [])

        assert expected_answer in bot.get_message()
