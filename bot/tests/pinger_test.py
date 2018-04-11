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


class TestPingerDelete:
    def test_delete_one_match(self, config, bot, update):
        username = "@test_two"
        match = "нумбер"
        pinger = Pinger(config)

        pinger.delete(bot, update, [username, match])

        assert "deleted" in bot.get_message()

    def test_delete_one_match_from_two_users(self, config, bot, update):
        username = "@test_two"
        username_two = "@user_three"
        match = "абырвалг"
        pinger = Pinger(config)

        pinger.delete(bot, update, [username, username_two, match])

        assert "deleted" in bot.get_message()

    def test_delete_false_match(self, config, bot, update):
        username = "@test_two"
        match = "failed"
        pinger = Pinger(config)

        pinger.delete(bot, update, [username, match])

        assert "not found" in bot.get_message()

    def test_delete_own_match(self, config, bot, update):
        match = "первого"
        pinger = Pinger(config)

        pinger.delete(bot, update, [match])

        assert "deleted" in bot.get_message()

    def test_delete_no_match(self, config, bot, update):
        pinger = Pinger(config)

        pinger.delete(bot, update, [])

        assert "Usage" in bot.get_message()

    def test_delete_another_user_no_admin(self, config, bot, update):
        update.set_message("",username="test_two")
        username = "@test_one"
        match = "первого"
        pinger = Pinger(config)

        pinger.delete(bot, update, [username, match])

        assert "reported" in bot.get_message()
