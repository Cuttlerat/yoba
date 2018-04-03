class MockUpdate:
    def __init__(self, text):
        self.message = MockMessage(text)

    def set_message(self, message):
        self.message = MockMessage(message)


class MockMessage:
    def __init__(self, input_text):
        self.text = input_text
