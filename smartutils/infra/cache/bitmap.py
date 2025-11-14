import sys
from typing import TYPE_CHECKING, Optional, Set

from smartutils.error.sys import LibraryUsageError
from smartutils.infra.cache.decode import DecodeBytes

try:
    from redis.asyncio import Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis


class RedisBitmap:
    """
    通用Redis Bitmap封装。按二进制位映射对象存在性、状态等。
    """

    def __init__(self, redis_cli: Redis, decode_bytes: DecodeBytes):
        self._redis: Redis = redis_cli
        self._decode_bytes = decode_bytes
        self._test_corner_case = False

    def _check(self):
        if self._decode_bytes.redis_decode_responses and not self._test_corner_case:
            raise LibraryUsageError(
                "RedisBitmap 不支持 decode_responses=True 的 Redis 客户端，请使用 decode_responses=False 的客户端实例化。"
            )

    async def set_bit(self, key: str, offset: int, flag: bool = True) -> None:
        """
        设置bitmap中指定bit的值
        :param key: bitmap键
        :param offset: bit位（0为起点）
        :param flag: True(1)/False(0)
        """
        self._check()
        await self._redis.setbit(key, offset, int(flag))

    async def get_bit(self, key: str, offset: int) -> bool:
        """
        获取bitmap中指定bit的当前值
        :return: True(1)/False(0)
        """
        result = await self._redis.getbit(key, offset)
        return bool(result)

    async def get_all_set_bits(
        self, key: str, max_offset: int = sys.maxsize
    ) -> Optional[Set[int]]:
        """
        获取bitmap中所有为 1 的bit下标（即所有set用户、资源编号等）。
        :param key: bitmap键
        :param max_offset: 最大遍历bit（业务方根据ID最大值传递)
        :return: 被置1的bit集合
        """
        self._check()
        bitmap = await self._redis.get(key)
        if not bitmap:
            return None
        if isinstance(bitmap, str):
            # 兼容String返回
            bitmap = bitmap.encode()
        result = set()
        for byte_index, byte in enumerate(bitmap):
            if not byte:
                continue
            for bit_index in range(8):
                idx = byte_index * 8 + bit_index
                if idx > max_offset:
                    return result
                if byte & (1 << (7 - bit_index)):
                    result.add(idx)
        return result
