from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Optional

from smartutils.error.factory import ExcDetailFactory
from smartutils.error.sys import CacheError
from smartutils.infra.cache.decode import DecodeBytes
from smartutils.log import logger

try:
    from redis.asyncio import Redis, ResponseError
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis, ResponseError


class SafeQueueStream:
    def __init__(self, redis_cli: Redis, decode_bytes: DecodeBytes):
        self._redis: Redis = redis_cli
        self._decode_bytes = decode_bytes

    async def ensure_stream_and_group(self, stream_name: str, group_name: str):
        try:
            await self._redis.xgroup_create(
                stream_name, group_name, id="0", mkstream=True
            )
        except ResponseError as e:
            if "BUSYGROUP Consumer Group name already exists" not in str(e):
                raise CacheError(ExcDetailFactory.get(e)) from None

    @asynccontextmanager
    async def xread_xack(
        self, stream: str, group: str, count: int = 1
    ) -> AsyncGenerator[Optional[dict], None]:
        """使用 with 语句读取并处理 Redis Stream，自动提交 ACK"""
        message_ids = set()
        try:
            await self.ensure_stream_and_group(stream, group)
            # print('messages================start',)
            # 从 Redis Stream 获取消息
            # TODO: 非阻塞方式有问题
            # messages = await self._redis.xread({stream: "0"}, count=count, block=1000)
            messages = await self._redis.xreadgroup(
                groupname=group,
                consumername="consumer",
                streams={stream: ">"},
                count=count,
                block=1000,
            )
            if len(messages) > count:
                logger.error("xread_xack get {} expect {}", len(messages), count)
            # print('messages================', messages)
            if not messages:
                yield None
                return
            logger.debug("xread_xack msgs: {}", messages)
            for message in messages:
                stream_name, messages_list = message
                for message_id, fields in messages_list:
                    message_ids.add(message_id)

                    fields = {
                        key.decode() if isinstance(key, bytes) else key: (
                            value.decode() if isinstance(value, bytes) else value
                        )
                        for key, value in fields.items()
                    }
                    yield fields
        except Exception as e:
            logger.exception("xread xack fail {}", e)
            yield None
        finally:
            # 在退出时提交 ACK
            for message_id in message_ids:
                await self._redis.xack(stream, group, message_id)
