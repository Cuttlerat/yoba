class MockUpdate:
    def __init__(self, text):
        self.message = MockMessage(text)

    def set_message(self, message, username=None):
        self.message = MockMessage(message, username)


class MockUser():
    def __init__(self, username="test_one"):
        self.username = username


class MockMessage:
    def __init__(self, input_text, username=None):
        self.text = input_text
        self.chat_id = -1
        if username is None:
            self.from_user = MockUser()
        else:
            self.from_user = MockUser(username)
        self.message_id = 123


class MockBot:
    def __init__(self):
        self.__sent_message = ""
        pass

    def send_message(self, chat_id, text, parse_mode="", reply_to_message_id=""):
        self.__sent_message = text

    def get_message(self):
        return self.__sent_message
