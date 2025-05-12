from dataclasses import dataclass
from typing import Tuple, Optional

import jwt

from smartutils.config import ConfKey
from smartutils.config.schema.token import TokenConf
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory
from smartutils.time import get_stamp_after

__all__ = ["User", "TokenHelper"]


@dataclass
class User:
    id: int
    name: str


@singleton
class TokenHelper:
    def __init__(self, conf: TokenConf):
        self._access_secret: str = conf.access_secret
        self._access_exp_sec: int = conf.access_exp_min * 60
        self._refresh_secret: str = conf.refresh_secret
        self._refresh_exp_sec: int = conf.refresh_exp_day * 24 * 60

    @staticmethod
    def _generate_token(user: User, secret: str, exp_sec: int) -> Tuple[str, int]:
        exp_time = int(get_stamp_after(second=exp_sec))

        token = jwt.encode(
            {"userid": user.id, "username": user.name, "exp": exp_time},
            secret,
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

    def token(self, user: User) -> Tuple[str, int, str, int]:
        access, access_exp = self._generate_token(
            user, self._access_secret, self._access_exp_sec
        )
        refresh, refresh_exp = self._generate_token(
            user, self._refresh_secret, self._refresh_exp_sec
        )
        return access, access_exp, refresh, refresh_exp

    def refresh(self, refresh_token) -> Optional[Tuple[str, int, str, int]]:
        payload = self.verify_token(refresh_token, self._refresh_secret)
        if not payload:
            return None
        user = User(payload["userid"], payload["username"])
        # access, access_exp = self._generate_token(
        #     user, self._access_secret, self._access_exp_sec
        # )
        access, access_exp, refresh, refresh_exp = self.token(user)
        return access, access_exp, refresh_token, payload["exp"]


@InfraFactory.register(ConfKey.TOKEN)
def init_token(conf):
    return TokenHelper(conf)
