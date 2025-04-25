import pytest
import yaml


# 构建一个完整的、合法的配置字典
def make_config_dict():
    return {
        'mysql': {
            'host': 'localhost',
            'port': 3306,
            'user': 'root',
            'passwd': '123456',
            'db': 'test_db',
        },
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0,
        },
        'kafka': {
            'bootstrap_servers': [
                {'host': 'localhost', 'port': 9092},
                {'host': '127.0.0.1', 'port': 9093}
            ],
            'client_id': 'unmanned',

        },
        'postgresql': {
            'host': '127.0.0.1',
            'port': 5432,
            'user': 'postgres',
            'passwd': '123456',
            'db': 'test_db',
        },
        'canal': {
            'host': '127.0.0.1',
            'port': 11111,
            'clients': [{'name': 'c1', 'client_id': '1', 'destination': 'd1'}]
        }
    }


def write_yaml(tmp_path, data):
    path = tmp_path / 'config.yaml'
    with open(path, 'w') as f:
        yaml.dump(data, f)
    return str(path)


def test_config_loads_all(tmp_path):
    # 写入合法配置
    conf_dict = make_config_dict()
    yaml_path = write_yaml(tmp_path, conf_dict)

    # 初始化全局 config
    from smartutils.config import init
    assert init(yaml_path) == True

    from smartutils.config import config

    # 检查所有字段被正确实例化
    assert config is not None
    assert config.mysql.url == 'mysql+asyncmy://root:123456@localhost:3306/test_db'
    assert config.redis.url == 'redis://localhost:6379'
    assert config.kafka.urls == ['localhost:9092', '127.0.0.1:9093']
    assert config.canal.clients[0].name == 'c1'


def test_config_missing_section(tmp_path):
    conf_dict = make_config_dict()
    # 删除 redis
    conf_dict.pop('redis')
    yaml_path = write_yaml(tmp_path, conf_dict)

    from smartutils.config import Config
    cfg = Config()
    cfg.load_conf(yaml_path)
    # redis 应该未被赋值
    assert not hasattr(cfg, 'redis') or cfg.redis is None


def test_config_invalid_section(tmp_path):
    conf_dict = make_config_dict()
    conf_dict['mysql']['port'] = 'not_a_port'  # 错误类型
    yaml_path = write_yaml(tmp_path, conf_dict)

    from smartutils.config import Config
    cfg = Config()
    with pytest.raises(Exception):
        cfg.load_conf(yaml_path)


def test_config_global_init(tmp_path, monkeypatch):
    conf_dict = make_config_dict()
    yaml_path = write_yaml(tmp_path, conf_dict)

    # 初始化全局 config
    from smartutils import config as config_module
    # 保证全局 config 被刷新
    config_module.config = None

    config_module.init(yaml_path)
    assert config_module.config.mysql.user == 'root'
