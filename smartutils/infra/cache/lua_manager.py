from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Dict, Optional, Sequence, Tuple

from smartutils.infra.cache.const import LUAS, LuaName
from smartutils.log import logger

try:
    from redis.asyncio import Redis
    from redis.commands.core import AsyncScript
    from redis.exceptions import ResponseError
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis
    from redis.commands.core import AsyncScript
    from redis.exceptions import ResponseError


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
            lua = redis_cli.register_script(LUAS[name])
            cls._luas[key] = lua
            return lua

    @classmethod
    async def call(
        cls,
        name: LuaName,
        redis_cli: Redis,
        keys: Optional[Sequence] = None,
        args: Optional[Sequence] = None,
    ):
        """
        调用脚本。自动注册/缓存Script对象，直接 await 脚本调用 keys/args。
        键值必须使用KEYS传递,集群分槽需要
        """
        # Redis 命令只能收字符串、二进制、数值、浮点，不支持 None/Null/nil 这种空类型作为参数传递。
        keys = [(k if k is not None else "") for k in (keys or [])]
        args = [(a if a is not None else "") for a in (args or [])]
        lua = await cls.get(name, redis_cli)
        try:
            return await lua(keys=keys or [], args=args or [])
        except ResponseError as e:
            logger.error(f"Lua script {name} execution error: {e}")
            raise e
