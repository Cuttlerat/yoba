import pytest

from config import Config
from models.models import create_table
from test.mocks import MockUpdate, MockBot


@pytest.fixture
def update():
    mock_update = MockUpdate("")
    return mock_update


@pytest.fixture
def bot():
    mock_bot = MockBot()
    return mock_bot


@pytest.fixture(scope="session")
def config():
    mock_config = Config("./config/config.test.yaml")
    create_table(mock_config)
    return mock_config
