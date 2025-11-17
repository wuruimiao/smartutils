from typing import TYPE_CHECKING, Any, List, Optional, Union

try:
    from redis.asyncio import Redis
except ImportError:
    ...
if TYPE_CHECKING:  # pragma: no cover
    from redis.asyncio import Redis


class ZSetHelper:
    @classmethod
    async def peek(
        cls,
        redis: Redis,
        zset: str,
        min_score: Optional[Union[int, float]] = None,
        max_score: Optional[Union[int, float]] = None,
        limit: int = 1,
    ) -> List[Any]:
        """
        查询 zset（有序集合）中指定 score 区间的任务成员，不移除，仅返回 member 列表。

        取值顺序说明：
        - 返回顺序为分数（score）从大到小（即：优先级高的、score大的在前）。
        - 若未指定 min_score/max_score，取 zset 中 score 最大的前 limit 个成员。
        - 若指定 score 区间，则取 [min_score, max_score] 闭区间内，score 最大的前 limit 个成员。

        :param zset: Redis 有序集合 key
        :param min_score: 最小 score，缺省时为负无穷（-inf）
        :param max_score: 最大 score，缺省时为正无穷（+inf）
        :param limit: 最多返回成员数
        :return: zset 指定区间、按从大到小排序的前 limit 个成员（不含分数）
        """
        # 默认只取最大优先级：zrevrange（分数从大到小排序，不带分数）
        if min_score is None and max_score is None:
            members = await redis.zrevrange(zset, 0, limit - 1)
        else:
            # 指定分数区间（闭区间），zrevrangebyscore 按 score 从大到小排序
            minp = min_score if min_score is not None else "-inf"
            maxp = max_score if max_score is not None else "+inf"
            members = await redis.zrevrangebyscore(zset, maxp, minp, start=0, num=limit)
        return members
