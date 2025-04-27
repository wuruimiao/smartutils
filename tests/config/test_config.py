import pytest
import yaml


@pytest.fixture(scope="session", autouse=True)
async def setup_config(tmp_path_factory):
    config_str = """
mysql:
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
  host: localhost
  port: 6379
  password: ""
  db: 0
  pool_size: 10
  connect_timeout: 10
  socket_timeout: 10
kafka:
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
  host: 127.0.0.1
  port: 11111
  clients:
    - name: c1
      client_id: "1234"
      destination: unmanned_task
    - name: unmanned_task
      client_id: "1234"
      destination: unmanned_task"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    print(config_file)
    return config_file


def test_config_loads_all(setup_config: str):
    from smartutils.config import init
    assert init(setup_config)

    from smartutils.config import get_config

    config = get_config()
    assert config is not None
    assert config.mysql.url == 'mysql+asyncmy://root:naobo@localhost:3306/test_db'
    assert config.redis.url == 'redis://localhost:6379'
    assert config.kafka.urls == ['localhost:19092', '127.0.0.1:9093']
    assert config.canal.clients[0].name == 'c1'
