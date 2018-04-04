import pytest

from handlers.helpers import prepare_message
from test.mocks import MockUpdate


@pytest.fixture
def update():
    mock_update = MockUpdate("")
    return mock_update


def test_prepare_message(update):
    update.set_message("Текст с БОЛЬШИМИ буквами и Ё")
    expected_text = "текст с большими буквами и е"

    edited_text = prepare_message(update)

    assert edited_text == expected_text
