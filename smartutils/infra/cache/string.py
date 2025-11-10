from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

from smartutils.infra.cache.lua_manager import LuaManager, LuaName

try:
    from redis.asyncio import Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis


class LuaOp(str, Enum):
    INCR = "incr"
    DECR = "decr"


class SafeString:
    def __init__(self, redis_cli: Redis):
        self._redis: Redis = redis_cli

    async def _num_op(self, op: LuaOp, key: str, ex: Optional[int] = None) -> str:
        """
        执行指定op的原子自增/自减操作
        :param op: StringOp.INCR or StringOp.DECR
        :return: 操作后的数值（字符串类型）
        """
        ex_str = str(ex) if ex else ""
        return await LuaManager.call(
            LuaName.INCR_DECR, self._redis, keys=[key], args=[op.value, ex_str]
        )

    async def incr(self, key: str, ex: Optional[int] = None) -> str:
        """
        原子自增计数器。
        """
        return await self._num_op(LuaOp.INCR, key, ex)

    async def decr(self, key: str, ex: Optional[int] = None) -> str:
        """
        原子自减计数器。
        """
        return await self._num_op(LuaOp.DECR, key, ex)
