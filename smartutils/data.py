import ipaddress
import json
import re

__all__ = ["dict_json", "check_ip", "check_domain", "check_port", "max_int", "min_int"]

import sys

DOMAIN_REGEX = re.compile(
    r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)"
    r"(\.(?!-)[A-Za-z0-9-]{1,63}(?<!-))*"
    r"\.[A-Za-z]{2,}$"
)


def dict_json(d, sort=False) -> str:
    return json.dumps(d, ensure_ascii=False, sort_keys=sort)


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


def max_int() -> int:
    return sys.maxsize


def min_int() -> int:
    return - sys.maxsize
