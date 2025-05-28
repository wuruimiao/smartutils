from smartutils.data import check_ip, check_domain, check_port, check_mail, check_phone, check_username
from smartutils.data.check import USERNAME_PATTERN, MAIL_PATTERN

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

def test_check_edge_cases():
    assert not check_ip(None)
    assert not check_ip("")
    assert not check_domain(None)
    assert not check_domain("")
    assert not check_port(None)
    assert not check_port("")
    assert not check_port("abc")

def test_check_mail():
    assert check_mail("user@example.com")
    assert check_mail("user.name+tag@example.com")
    assert check_mail("user123@sub.example.com")
    assert not check_mail("invalid.email")
    assert not check_mail("@example.com")
    assert not check_mail("user@")
    assert not check_mail("user@.com")
    assert not check_mail("")
    assert not check_mail(None)

def test_check_phone():
    assert check_phone("12345678901")
    assert check_phone("123456789012")
    assert not check_phone("abc")
    assert not check_phone("")
    assert not check_phone(None)
    assert not check_phone("123a456")

def test_check_username():
    assert check_username("user123")
    assert check_username("USER123")
    assert check_username("abc")
    assert not check_username("user-123")
    assert not check_username("user@123")
    assert not check_username("")
    assert not check_username(None)
    assert not check_username(" user123")

def test_patterns():
    # 验证正则模式字符串存在且格式正确
    assert USERNAME_PATTERN.startswith("^")
    assert USERNAME_PATTERN.endswith("$")
    assert MAIL_PATTERN.startswith("^")
    assert MAIL_PATTERN.endswith("$")