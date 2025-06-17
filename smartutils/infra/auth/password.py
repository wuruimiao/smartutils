from typing import TYPE_CHECKING, Tuple

from smartutils.config import ConfKey
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory

try:
    import bcrypt
except ImportError:
    pass

if TYPE_CHECKING:
    import bcrypt

__all__ = ["PasswordHelper"]

msg = "smartutils.infra.auth.password.PasswordHelper depend on bcrypt, install before use."


@singleton
class PasswordHelper:
    @staticmethod
    def hash_password(plain_password: str) -> Tuple[str, str]:
        assert bcrypt, msg
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return salt.decode("utf-8"), hashed_password.decode("utf-8")

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        assert bcrypt, msg
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )


@InfraFactory.register(ConfKey.PASSWORD, need_conf=False)
def _(conf):
    return PasswordHelper()
