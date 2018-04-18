import pytest
from odr.container import register_as

from config import Config
from handlers.pinger import Pinger
from mocks.mocks import MockUpdate, MockBot
from models.models import create_table, fill_db_with_mock_data


@pytest.fixture
def update():
    mock_update = MockUpdate("")
    return mock_update


@pytest.fixture
def bot():
    mock_bot = MockBot()
    return mock_bot


@pytest.fixture(scope="session")
def config(tmpdir_factory):
    database_dir = tmpdir_factory.mktemp('data').join('tests.db')
    mock_config = Config("./config/config.test.yaml", database_path=str(database_dir))
    create_table(mock_config)
    fill_db_with_mock_data(mock_config)
    return mock_config


@pytest.fixture
def pinger(config):
    register_as(config, Config)
    pinger = Pinger()
    return pinger
