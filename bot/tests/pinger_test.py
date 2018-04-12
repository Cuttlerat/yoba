from handlers.new_pinger import Pinger


class TestPingerShow:
    def test_show_empty(self, config, bot, update):
        expected_message = "первого"
        pinger = Pinger(config)

        pinger.show(bot, update, [])

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
        expected_message = "Usage:"
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
        expected = "only allowed"
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
        update.set_message("", username="test_two")
        username = "@test_one"
        match = "первого"
        pinger = Pinger(config)

        pinger.delete(bot, update, [username, match])

        assert "Deleting" in bot.get_message()


class TestPingerAdd:
    def test_add_for_me_not_admin(self, config, bot, update):
        update.set_message("", username="test_two")
        match = "тулук"
        pinger = Pinger(config)

        pinger.add(bot, update, [match])

        assert "added" in bot.get_message()

    def test_add_not_for_me_not_admin(self, config, bot, update):
        update.set_message("", username="test_two")
        username = "@test_one"
        match = "тулук"
        pinger = Pinger(config)

        pinger.add(bot, update, [username, match])

    def test_add_no_matches(self, config, bot, update):
        update.set_message("", username="test_two")
        pinger = Pinger(config)

        pinger.add(bot, update, [])

        assert "Usage" in bot.get_message()

    def test_add_eleventh_match_no_admin(self, config, bot, update):
        update.set_message("", username="test_add")
        username = "@test_add"
        match = "eleven"

        pinger = Pinger(config)

        pinger.add(bot, update, [username, match])

        assert "only 10 matches" in bot.get_message()

    def test_add_eleventh_match_admin(self, config, bot, update):
        username = "@test_add"
        match = "eleven"

        pinger = Pinger(config)

        pinger.add(bot, update, [username, match])

        assert "has been added" in bot.get_message()
