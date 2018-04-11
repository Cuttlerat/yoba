from handlers.new_pinger import Pinger


class TestPinger:
    def test_show_empty(self, config, bot, update):
        expected_message = "первого"
        pinger = Pinger(config)

        pinger.show(bot, update, [])

        assert expected_message in bot.get_message()

    def test_show_me(self, config, bot, update):
        expected_message = "первого"
        pinger = Pinger(config)

        pinger.show(bot, update, ["me"])

        assert expected_message in bot.get_message()

    def test_show_username(self, config, bot, update):
        expected_message = "второго"
        pinger = Pinger(config)

        pinger.show(bot, update, ["@test_two"])

        assert expected_message in bot.get_message()

    def test_show_no_exist_username(self, config, bot, update):
        expected_message = "No such user"
        pinger = Pinger(config)

        pinger.show(bot, update, ["@test_none"])

        assert expected_message in bot.get_message()

    def test_show_no_nickname(self, config, bot, update):
        expected_message = "Usage: "
        pinger = Pinger(config)

        pinger.show(bot, update, ["fail"])

        assert expected_message in bot.get_message()
