import pytest


@pytest.fixture(scope="function")
async def setup_config(tmp_path_factory):
    config_str = """
mysql:
  default:
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
postgresql:
  default:
    host: localhost
    port: 5432
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
redis:
  default:
    host: localhost
    port: 6379
    password: ""
    db: 0
    pool_size: 10
    connect_timeout: 10
    socket_timeout: 10
kafka:
  default:
    bootstrap_servers:
      - host: localhost
        port: 19092
      - host: 127.0.0.1
        port: 9093
    client_id: unmanned
    acks: all
    compression_type: zstd
    max_batch_size: 16384
    linger_ms: 0
    request_timeout_ms: 1000
    retry_backoff_ms: 100
canal:
  default:
    host: 127.0.0.1
    port: 11111
    clients:
      - name: c1
        client_id: "1234"
        destination: unmanned_task
      - name: unmanned_task
        client_id: "1234"
        destination: unmanned_task
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""

    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    yield config_file


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


def test_config_loads_all(setup_config: str):
    from smartutils.config import Config

    assert Config.init(setup_config)

    config = Config.get_config()
    assert config is not None
    assert (
        config.get("mysql")["default"].url  # type: ignore
        == "mysql+asyncmy://root:naobo@localhost:3306/test_db"
    )
    assert (
        config.get("postgresql")["default"].url  # type: ignore
        == "postgresql+asyncpg://root:naobo@localhost:5432/test_db"
    )
    assert config.get("redis")["default"].url == "redis://localhost:6379"  # type: ignore
    assert config.get("kafka")["default"].urls == ["localhost:19092", "127.0.0.1:9093"]  # type: ignore
    assert config.get("canal")["default"].clients[0].name == "c1"  # type: ignore
    assert config.project.name == "auth"
    assert config.project.description == "test_auth"
    assert config.project.version == "0.0.1"


def test_config_empty(setup_conf_empty: str):
    from smartutils.config import Config
    from smartutils.error.sys import ConfigError

    with pytest.raises(ConfigError):
        Config.init(setup_conf_empty)


def test_config_no_conf_class(setup_no_conf_class_config: str):
    from smartutils.config import Config

    Config.init(setup_no_conf_class_config)


def test_config_no_default(setup_no_conf_default_config: str):
    from smartutils.config import Config

    Config.init(setup_no_conf_default_config)


def test_config_no_config_file(setup_config):
    from smartutils.config import Config

    Config.init("no_config")


def test_config_no_config(setup_config):
    from smartutils.config import Config
    from smartutils.error.sys import LibraryUsageError

    Config.reset()
    with pytest.raises(LibraryUsageError):
        Config.get_config()


def test_project_conf_inherit(setup_config: str):
    from smartutils.config import ConfFactory, Config, ConfKey, ProjectConf

    @ConfFactory.register(ConfKey.PROJECT, multi=False, require=False)
    class MyProjectConf(ProjectConf):
        key: str

    Config.init(setup_config)
    conf = Config.get_config()
    assert conf.project.key == "test_key"
