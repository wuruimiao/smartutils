from dataclasses import dataclass
from typing import Tuple, Optional

from smartutils.log import logger

try:
    import jwt
except ImportError:
    logger.debug("smartutils.infra.auth.token.TokenHelper depend on jwt, install first.")
    jwt = None

from smartutils.config import ConfKey
from smartutils.config.schema.token import TokenConf
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory
from smartutils.time import get_stamp_after

__all__ = ["User", "Token", "TokenHelper"]


@dataclass
class User:
    id: int
    name: str


@dataclass
class Token:
    token: str
    exp: int


@singleton
class TokenHelper:
    def __init__(self, conf: TokenConf):
        self._access_secret: str = conf.access_secret
        self._access_exp_sec: int = conf.access_exp_min * 60
        self._refresh_secret: str = conf.refresh_secret
        self._refresh_exp_sec: int = conf.refresh_exp_day * 24 * 60

    @staticmethod
    def _generate_token(user: User, secret: str, exp_sec: int) -> Token:
        exp_time = int(get_stamp_after(second=exp_sec))

        token = jwt.encode(
            {"userid": user.id, "username": user.name, "exp": exp_time},
            secret,
            algorithm="HS256",
        )
        return Token(token, exp_time)

    @staticmethod
    def verify_token(token: str, secret: str):
        try:
            payload = jwt.decode(token, secret, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def token(self, user: User) -> Tuple[Token, Token]:
        access_t = self._generate_token(user, self._access_secret, self._access_exp_sec)
        refresh_t = self._generate_token(
            user, self._refresh_secret, self._refresh_exp_sec
        )
        return access_t, refresh_t

    def refresh(self, refresh_token) -> Optional[Tuple[Token, Token]]:
        payload = self.verify_token(refresh_token, self._refresh_secret)
        if not payload:
            return None
        user = User(payload["userid"], payload["username"])
        access_t = self._generate_token(user, self._access_secret, self._access_exp_sec)
        # 默认刷新token不延期
        # access_t, refresh_t = self.token(user)
        return access_t, Token(refresh_token, payload["exp"])


@InfraFactory.register(ConfKey.TOKEN)
def _(conf):
    return TokenHelper(conf)
