from handlers.new_pinger import Pinger


class TestPingerShow:
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


class TestPingerShowAll:
    def test_show_all_admin(self, config, bot, update):
        expected = "первого"
        pinger = Pinger(config)

        pinger.show_all(bot, update)

        assert expected in bot.get_message()

    def test_show_all_not_admin(self, config, bot, update):
        update.set_message("", username="test_two")
        expected = "allowed only"
        pinger = Pinger(config)

        pinger.show_all(bot, update)

        assert expected in bot.get_message()
