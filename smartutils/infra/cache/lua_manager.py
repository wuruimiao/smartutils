from __future__ import annotations

import asyncio
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from smartutils.infra.cache.const import INCR_DECR_SCRIPT

try:
    from redis.asyncio import Redis
    from redis.commands.core import AsyncScript
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis
    from redis.commands.core import AsyncScript


class LuaName(Enum):
    INCR_DECR = "incr_decr"


class LuaOp(str, Enum):
    INCR = "incr"
    DECR = "decr"


_LUAS = {
    LuaName.INCR_DECR: INCR_DECR_SCRIPT,
}


class LuaManager:
    _luas: Dict[Tuple[int, LuaName], AsyncScript] = {}
    _lock = asyncio.Lock()

    @classmethod
    async def get(cls, name: LuaName, redis_cli: Redis) -> AsyncScript:
        """
        获取某个脚本对象。已注册直接返回，未注册且存在脚本内容则自动注册。
        """
        key = (id(redis_cli), name)
        if name in cls._luas:
            return cls._luas[key]
        async with cls._lock:
            if name in cls._luas:
                return cls._luas[key]
            lua = redis_cli.register_script(_LUAS[name])
            cls._luas[key] = lua
            return lua

    @classmethod
    async def call(
        cls,
        name: LuaName,
        redis_cli: Redis,
        keys: Optional[List] = None,
        args: Optional[List] = None,
    ):
        """
        调用脚本。自动注册/缓存Script对象，直接 await 脚本调用 keys/args。
        """
        lua = await cls.get(name, redis_cli)
        return await lua(keys=keys or [], args=args or [])
