import ipaddress
import re

from smartutils.data.base import is_num

DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*"
    r"\.[A-Za-z]{2,}$"
)
USERNAME_PATTERN = r"^[a-zA-Z0-9]+$"
MAIL_PATTERN = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

_USERNAME_REGEX = re.compile(USERNAME_PATTERN)
_MAIL_REGEX = re.compile(MAIL_PATTERN)


def check_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def check_domain(domain: str) -> bool:
    return not not DOMAIN_REGEX.match(domain)


def check_port(port: int) -> bool:
    return 1 <= port <= 65535


def check_mail(s: str) -> bool:
    return bool(_MAIL_REGEX.fullmatch(s))


def check_phone(s: str) -> bool:
    return is_num(s)


def check_username(s: str) -> bool:
    return bool(_USERNAME_REGEX.fullmatch(s))
