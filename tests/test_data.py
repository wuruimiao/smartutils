from smartutils.data import dict_json, check_ip, check_domain, check_port


def test_dict_json():
    d = {"b": 2, "a": 1}
    # 默认不排序
    assert dict_json(d) == '{"b": 2, "a": 1}'
    # 排序
    assert dict_json(d, sort=True) == '{"a": 1, "b": 2}'


def test_check_ip():
    assert check_ip("127.0.0.1")
    assert check_ip("::1")
    assert check_ip("192.168.1.1")
    assert not check_ip("999.999.999.999")
    assert not check_ip("abcd")
    assert not check_ip("")


def test_check_domain():
    assert check_domain("example.com")
    assert check_domain("sub.domain.com")
    assert not check_domain("-example.com")
    assert not check_domain("example-.com")
    assert not check_domain("example")
    assert not check_domain("example..com")
    assert not check_domain("ex@mple.com")
    assert not check_domain("")


def test_check_port():
    assert check_port(80)
    assert check_port(65535)
    assert not check_port(0)
    assert not check_port(65536)
    assert not check_port(-1)
