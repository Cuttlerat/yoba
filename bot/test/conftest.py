import pytest

from test.mocks import MockUpdate, MockBot


@pytest.fixture
def update():
    mock_update = MockUpdate("")
    return mock_update

@pytest.fixture
def bot():
    mock_bot = MockBot()
    return mock_bot