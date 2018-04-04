class MockUpdate:
    def __init__(self, text):
        self.message = MockMessage(text)

    def set_message(self, message):
        self.message = MockMessage(message)


class MockMessage:
    def __init__(self, input_text):
        self.text = input_text
        self.chat_id = -0


class MockBot:
    def __init__(self):
        self.__sent_message = ""
        pass

    def send_message(self, chat_id, text, parse_mode=""):
        self.__sent_message = text

    def get_message(self):
        return self.__sent_message
