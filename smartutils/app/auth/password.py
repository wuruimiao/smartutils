from typing import Tuple

import bcrypt


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


password_helper = PasswordHelper()
