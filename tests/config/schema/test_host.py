import pytest
from pydantic import ValidationError

from smartutils.config.schema.host import HostConf


@pytest.mark.parametrize(
    "host, port",
    [
        ("127.0.0.1", 8080),
        ("localhost", 80),
        ("example.com", 65535),
    ],
)
def test_hostconf_valid(host, port):
    conf = HostConf(host=host, port=port)
    assert conf.host == host
    assert conf.port == port


@pytest.mark.parametrize(
    "host",
    [
        "",  # 为空
        None,
    ],
)
def test_hostconf_invalid_host(host):
    with pytest.raises(ValidationError) as exc:
        HostConf(host=host, port=8080)
    assert "host不能为空" in str(exc.value) or "host" in str(exc.value)


@pytest.mark.parametrize(
    "port",
    [
        0,  # 太小
        65536,  # 太大
        -1,  # 负数
        None,  # 为空
    ],
)
def test_hostconf_invalid_port(port):
    with pytest.raises(ValidationError) as exc:
        HostConf(host="127.0.0.1", port=port)
    assert "port必须在1-65535之间" in str(exc.value) or "port" in str(exc.value)


def test_the_url():
    conf = HostConf(host="127.0.0.1", port=3306)
    assert conf.the_url == "127.0.0.1:3306"

    conf2 = HostConf(host="localhost", port=8080)
    assert conf2.the_url == "localhost:8080"


@pytest.mark.parametrize(
    "host, port",
    [
        ("127.0.0.1", 8080),
        ("localhost", 80),
        ("example.com", 65535),
    ],
)
def test_custom_dump_excludes_host_port(host, port):
    conf = HostConf(host=host, port=port)
    dumped = conf.model_dump()
    assert dumped["host"] == host
    assert dumped["port"] == port
