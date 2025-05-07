from dataclasses import dataclass
from typing import Tuple, Optional

import jwt

from smartutils.time import get_stamp_after


@dataclass
class User:
    id: int
    name: str


@dataclass
class Secret:
    exp_sec: int
    secret: str


class TokenHelper:
    @staticmethod
    def _generate_token(user: User, secret: Secret) -> Tuple[str, int]:
        exp_time = int(get_stamp_after(second=secret.exp_sec))

        token = jwt.encode(
            {"userid": user.id, "username": user.name, "exp": exp_time},
            secret.secret,
            algorithm="HS256",
        )
        return token, exp_time

    @staticmethod
    def verify_token(token: str, secret: str):
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def token(
        self, user: User, access_secret: Secret, refresh_secret: Secret
    ) -> Tuple[str, int, str, int]:
        access, access_exp = self._generate_token(user, access_secret)
        refresh, refresh_exp = self._generate_token(user, refresh_secret)
        return access, access_exp, refresh, refresh_exp

    def refresh(
        self, refresh_token, access_secret: Secret, refresh_secret: Secret
    ) -> Optional[Tuple[str, int, str, int]]:
        payload = self.verify_token(refresh_token, refresh_secret.secret)
        if not payload:
            return None
        user = User(payload["userid"], payload["username"])
        access, access_exp = self._generate_token(user, access_secret)
        return access, access_exp, refresh_token, payload["exp"]


token_helper = TokenHelper()
