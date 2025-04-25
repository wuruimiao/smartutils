import pytest
from pydantic import ValidationError

from smartutils.config.schema.canal import (CanalClientConf, CanalConf)


@pytest.fixture
def host_conf_dict():
    # 用于继承CanalConf的HostConf字段
    return {
        "host": "127.0.0.1",
        "port": 11111
    }


def test_canal_client_conf_valid():
    conf = CanalClientConf(name="test", client_id='123', destination="dest")
    assert conf.name == "test"
    assert conf.client_id == "123"
    assert conf.destination == "dest"


def test_canal_client_conf_client_id_str():
    conf = CanalClientConf(name="test", client_id="abc", destination="dest")
    assert conf.client_id == "abc"


def test_canal_client_conf_client_id_none():
    with pytest.raises(ValidationError) as exc:
        CanalClientConf(name="test", client_id=None, destination="dest")
    assert "Input should be a valid string" in str(exc.value)


def test_canal_client_conf_destination_empty_str():
    with pytest.raises(ValidationError) as exc:
        CanalClientConf(name='test', destination=' ', client_id='123')
    assert 'destination must be non-empty strings' in str(exc.value)


def test_canal_client_conf_client_id_empty_str():
    with pytest.raises(ValidationError) as exc:
        CanalClientConf(name='test', destination='123', client_id='    ')
    assert 'client_id must be non-empty strings' in str(exc.value)


def test_canal_client_conf_name_empty_str():
    with pytest.raises(ValidationError) as exc:
        CanalClientConf(name=' ', destination='123', client_id='123')
    assert 'name must be non-empty strings' in str(exc.value)


def test_canal_conf_valid(host_conf_dict):
    clients = [
        {"name": "n1", "client_id": '1', "destination": "dest1"},
        {"name": "n2", "client_id": "2", "destination": "dest2"}
    ]
    conf = CanalConf(**host_conf_dict, clients=clients)
    assert conf.port == 11111
    assert len(conf.clients) == 2
    assert conf.clients[0].client_id == "1"
    assert conf.clients[1].client_id == "2"


def test_canal_conf_invalid_clients(host_conf_dict):
    # clients 为空列表是允许的（如有特殊需求可自定义校验）
    conf = CanalConf(**host_conf_dict, clients=[])
    assert conf.clients == []

    # clients 不是列表或元素不合法
    with pytest.raises(ValidationError):
        CanalConf(**host_conf_dict, clients=None)
    with pytest.raises(ValidationError):
        CanalConf(**host_conf_dict, clients=[{"name": "", "client_id": 1, "destination": "d"}])


def test_canal_conf_inherit_hostconf_invalid():
    # host字段非法
    with pytest.raises(ValidationError):
        CanalConf(host="", port=11111, clients=[])
    with pytest.raises(ValidationError):
        CanalConf(host=None, port=11111, clients=[])


def test_canal_conf_port_override(host_conf_dict):
    conf_dict = host_conf_dict.copy()
    conf_dict["port"] = 22222
    conf = CanalConf(**conf_dict, clients=[])
    assert conf.port == 22222
