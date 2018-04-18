from handlers.pinger import Pinger


class TestPingerShow:
    def test_show_empty(self, pinger, bot, update):
        expected_message = "первого"

        pinger.show(bot, update, [])

        assert expected_message in bot.get_message()

    def test_show_username(self, pinger, bot, update):
        expected_message = "второго"

        pinger.show(bot, update, ["@test_two"])

        assert expected_message in bot.get_message()

    def test_show_no_exist_username(self, pinger, bot, update):
        expected_message = "No such user"

        pinger.show(bot, update, ["@test_none"])

        assert expected_message in bot.get_message()

    def test_show_no_nickname(self, pinger, bot, update):
        expected_message = "Usage:"

        pinger.show(bot, update, ["fail"])

        assert expected_message in bot.get_message()


class TestPingerShowAll:
    def test_show_all_admin(self, pinger, bot, update):
        expected = "первого"

        pinger.show_all(bot, update)

        assert expected in bot.get_message()

    def test_show_all_not_admin(self, pinger, bot, update):
        update.set_message("", username="test_two")
        expected = "only allowed"

        pinger.show_all(bot, update)

        assert expected in bot.get_message()


class TestPingerDelete:
    def test_delete_one_match(self, pinger, bot, update):
        username = "@test_two"
        match = "нумбер"

        pinger.delete(bot, update, [username, match])

        assert "deleted" in bot.get_message()

    def test_delete_one_match_from_two_users(self, pinger, bot, update):
        username = "@test_two"
        username_two = "@user_three"
        match = "абырвалг"

        pinger.delete(bot, update, [username, username_two, match])

        assert "deleted" in bot.get_message()

    def test_delete_false_match(self, pinger, bot, update):
        username = "@test_two"
        match = "failed"

        pinger.delete(bot, update, [username, match])

        assert "not found" in bot.get_message()

    def test_delete_own_match(self, pinger, bot, update):
        match = "первого"

        pinger.delete(bot, update, [match])

        assert "deleted" in bot.get_message()

    def test_delete_no_match(self, pinger, bot, update):
        pinger.delete(bot, update, [])

        assert "Usage" in bot.get_message()

    def test_delete_another_user_no_admin(self, pinger, bot, update):
        update.set_message("", username="test_two")
        username = "@test_one"
        match = "первого"

        pinger.delete(bot, update, [username, match])

        assert "Deleting" in bot.get_message()


class TestPingerAdd:
    def test_add_for_me_not_admin(self, pinger, bot, update):
        update.set_message("", username="test_two")
        match = "тулук"

        pinger.add(bot, update, [match])

        assert "added" in bot.get_message()

    def test_add_not_for_me_not_admin(self, pinger, bot, update):
        update.set_message("", username="test_two")
        username = "@test_one"
        match = "тулук"

        pinger.add(bot, update, [username, match])

    def test_add_no_matches(self, pinger, bot, update):
        update.set_message("", username="test_two")

        pinger.add(bot, update, [])

        assert "Usage" in bot.get_message()

    def test_add_eleventh_match_no_admin(self, pinger, bot, update):
        update.set_message("", username="test_add")
        username = "@test_add"
        match = "eleven"

        pinger.add(bot, update, [username, match])

        assert "only 10 matches" in bot.get_message()

    def test_add_eleventh_match_admin(self, pinger, bot, update):
        username = "@test_add"
        match = "eleven"

        pinger.add(bot, update, [username, match])

        assert "has been added" in bot.get_message()


class TestPingerDrop:
    def test_drop_from_admin(self, pinger, bot, update):
        username = "@for_delete"

        pinger.drop(bot, update, [username])

        assert "deleted" in bot.get_message()

    def test_drop_false_username(self, pinger, bot, update):
        username = "@false_user"

        pinger.drop(bot, update, [username])

        assert "not found" in bot.get_message()

    def test_drop_no_admin(self, pinger, bot, update):
        update.set_message("", username="not_admin")
        username = "@some_user"

        pinger.drop(bot, update, [username])

        assert "allowed for admins" in bot.get_message()

    def test_drop_empty(self, pinger, bot, update):
        pinger.drop(bot, update, [])

        assert "Usage" in bot.get_message()
