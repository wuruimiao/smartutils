import pytest
from pydantic import ValidationError

from smartutils.config.schema.canal import CanalClientConf, CanalConf


@pytest.fixture
def host_conf_dict():
    return {"host": "127.0.0.1", "port": 11111}


def valid_canal_client_conf():
    return {
        "name": "test_name",
        "client_id": "test_client_id",
        "destination": "test_destination",
    }


def test_canal_client_conf_valid():
    conf = CanalClientConf(**valid_canal_client_conf())
    assert conf.name == "test_name"
    assert conf.client_id == "test_client_id"
    assert conf.destination == "test_destination"


@pytest.mark.parametrize("field", ["name", "destination", "client_id"])
def test_canal_client_conf_none(field):
    conf_dict = valid_canal_client_conf()
    with pytest.raises(ValidationError) as exc:
        conf_dict[field] = None
        CanalClientConf(**conf_dict)
    assert "Input should be a valid string" in str(exc.value) and field in str(
        exc.value
    )


@pytest.mark.parametrize("field", ["name", "destination", "client_id"])
@pytest.mark.parametrize("value", ["", " ", "\t", "\t\n"])
def test_canal_client_conf_empty_str(field, value):
    conf_dict = valid_canal_client_conf()
    with pytest.raises(ValidationError) as exc:
        conf_dict[field] = value
        CanalClientConf(**conf_dict)
    assert "String should have at least 1 character" in str(exc.value) and field in str(
        exc.value
    )


def test_canal_conf_valid(host_conf_dict):
    clients = [
        {"name": "n1", "client_id": "1", "destination": "dest1"},
        {"name": "n2", "client_id": "2", "destination": "dest2"},
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
        CanalConf(
            **host_conf_dict, clients=[{"name": "", "client_id": 1, "destination": "d"}]
        )


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
