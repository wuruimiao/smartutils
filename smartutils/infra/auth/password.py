from typing import Tuple

try:
    import bcrypt
except ImportError:
    bcrypt = None

from smartutils.config import ConfKey
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory
from smartutils.error.sys import LibraryUsageError

__all__ = ["PasswordHelper"]


@singleton
class PasswordHelper:
    @staticmethod
    def hash_password(plain_password: str) -> Tuple[str, str]:
        if not bcrypt:
            raise LibraryUsageError("PasswordHelper depend on bcrypt.")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return salt.decode("utf-8"), hashed_password.decode("utf-8")

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        if not bcrypt:
            raise LibraryUsageError("PasswordHelper depend on bcrypt.")
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )


@InfraFactory.register(ConfKey.PASSWORD, need_conf=False)
def _(conf):
    return PasswordHelper()
