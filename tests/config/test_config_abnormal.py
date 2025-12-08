import pytest

from smartutils.config.const import ConfKey


@pytest.fixture(scope="function")
async def setup_no_conf_class_config(tmp_path_factory):
    config_str = """
no_conf_class:
  default:
    a: 1
project:
  name: auth
  id: 0"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_invalid_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    yield config_file


@pytest.fixture(scope="function")
async def setup_no_conf_default_config(tmp_path_factory):
    config_str = """
mysql:
  no_default:
    host: localhost
    port: 3306
    user: root
    passwd: naobo
    db: test_db
    pool_size: 10
    max_overflow: 5
    pool_timeout: 30
    pool_recycle: 3600
    echo: false
    echo_pool: false
    connect_timeout: 10
    execute_timeout: 10
project:
  name: auth
  id: 0"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_no_default_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    yield config_file


@pytest.fixture(scope="function")
async def setup_conf_empty(tmp_path_factory):
    config_str = """"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_no_default_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    yield config_file


def test_config_empty(setup_conf_empty: str):
    from smartutils.config import Config

    Config.init(setup_conf_empty)
    assert Config.get_config() is not None
    assert Config.get_config()._config == {}
    assert Config.get_config()._instances != {}
    assert Config.get_config().get(ConfKey.PROJECT) is not None


def test_config_no_conf_class(setup_no_conf_class_config: str):
    from smartutils.config import Config

    Config.init(setup_no_conf_class_config)


def test_config_no_default(setup_no_conf_default_config: str):
    from smartutils.config import Config

    Config.init(setup_no_conf_default_config)


def test_config_no_config_file():
    from smartutils.config import Config

    Config.init("no_config")


def test_config_no_config():
    from smartutils.config import Config
    from smartutils.error.sys import LibraryUsageError

    Config.reset()
    with pytest.raises(LibraryUsageError):
        Config.get_config()
