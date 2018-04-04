from handlers.helpers import prepare_message, start, bug


class TestHelpers:
    def test_prepare_message(self, update):
        update.set_message("Текст с БОЛЬШИМИ буквами и Ё")
        expected_text = "текст с большими буквами и е"

        edited_text = prepare_message(update)

        assert edited_text == expected_text

    def test_start(self, bot, update):
        expected_text = "This is my first bot on Python."

        start(bot, update)

        assert expected_text in bot.get_message()

    def test_bug(self, bot, update):
        expected_text = "Please report it here"

        bug(bot, update)

        assert expected_text in bot.get_message()
