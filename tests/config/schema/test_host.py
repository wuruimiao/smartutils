import pytest
from pydantic import ValidationError

from smartutils.config.schema.host import HostConf


# ---- 正确用例 ----

@pytest.mark.parametrize(
    "host, port",
    [
        ("127.0.0.1", 8080),
        ("localhost", 80),
        ("example.com", 65535),
    ]
)
def test_hostconf_valid(host, port):
    conf = HostConf(host=host, port=port)
    assert conf.host == host
    assert conf.port == port


# ---- host 非法用例 ----

@pytest.mark.parametrize(
    "host",
    [
        "",  # 为空
        "invalid_host",  # 不是合法域名/IP/localhost
        "256.256.1.1",  # 非法IP
        None,
    ]
)
def test_hostconf_invalid_host(host):
    with pytest.raises(ValidationError) as exc:
        HostConf(host=host, port=8080)
    assert "host不能为空" in str(exc.value) or "host" in str(exc.value)


# ---- port 非法用例 ----

@pytest.mark.parametrize(
    "port",
    [
        0,  # 太小
        65536,  # 太大
        -1,  # 负数
        None,  # 为空
    ]
)
def test_hostconf_invalid_port(port):
    with pytest.raises(ValidationError) as exc:
        HostConf(host="127.0.0.1", port=port)
    assert "port必须在1-65535之间" in str(exc.value) or "port" in str(exc.value)
