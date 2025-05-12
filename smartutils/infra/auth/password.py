from typing import Tuple

import bcrypt

from smartutils.config import ConfKey
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory


@singleton
class PasswordHelper:
    @staticmethod
    def hash_password(plain_password: str) -> Tuple[str, str]:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
        return salt.decode("utf-8"), hashed_password.decode("utf-8")

    @staticmethod
    def check_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )


@InfraFactory.register(ConfKey.PASSWORD, need_conf=False)
def init_password(conf):
    return PasswordHelper()
