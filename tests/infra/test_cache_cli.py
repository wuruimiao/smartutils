import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import smartutils.infra.cache.cli as cachemod


@pytest.fixture
def redis_conf():
    class Conf:
        url = "redis://localhost/0"
        kw = {}

    return Conf()


@pytest.fixture
def async_cli():
    cli = cachemod.AsyncRedisCli.__new__(cachemod.AsyncRedisCli)
    cli._redis = AsyncMock()
    cli._pool = AsyncMock()
    cli._name = "test"
    return cli


async def test_ping_ok_and_fail(async_cli):
    async_cli._redis.ping.return_value = True
    assert await async_cli.ping() is True
    async_cli._redis.ping.side_effect = Exception("fail")
    assert await async_cli.ping() is False


async def test_set_get_delete(async_cli):
    async_cli._redis.set.return_value = True
    assert await async_cli.set("k", "v", expire=2) is True
    async_cli._redis.get.return_value = "v"
    v = await async_cli.get("k")
    assert v == "v"
    async_cli._redis.delete.return_value = 1
    assert await async_cli.delete("k1", "k2") == 1


async def test_incr_decr(async_cli):
    async_cli._redis.eval.return_value = 11
    assert await async_cli.incr("cnt", expire=2) == 11
    assert await async_cli.decr("cnt", expire=None) == 11


async def test_set_ops(async_cli):
    async_cli._redis.sadd.return_value = 1
    assert await async_cli.sadd("s", 1, 2) == 1
    async_cli._redis.srem.return_value = 2
    assert await async_cli.srem("s", 1, 2) == 2
    async_cli._redis.scard.return_value = 5
    assert await async_cli.scard("s") == 5


async def test_list_ops(async_cli):
    async_cli._redis.llen.return_value = 3
    assert await async_cli.llen("l") == 3
    async_cli._redis.rpush.return_value = 5
    assert await async_cli.rpush("l", "a", "b") == 5
    async_cli._redis.lrange.return_value = ["a", "b"]
    assert await async_cli.lrange("l", 0, 1) == ["a", "b"]


async def test_zset_ops(async_cli):
    async_cli._redis.zadd.return_value = 1
    assert await async_cli.zadd("z", "k", 9) == 1
    assert await async_cli.zadd_multi("z", {"a": 1, "b": 2}) == 1
    async_cli._redis.zcard.return_value = 2
    assert await async_cli.zcard("z") == 2
    async_cli._redis.zrange.return_value = ["a", "b"]
    assert await async_cli.zrange("z", 0, 1, withscores=True) == ["a", "b"]
    async_cli._redis.zrangebyscore.return_value = ["a"]
    assert await async_cli.zrangebyscore("z", 0, 10, withscores=False) == ["a"]
    async_cli._redis.zrem.return_value = 1
    assert await async_cli.zrem("z", "a", "b") == 1


async def test_close(async_cli):
    await async_cli.close()
    async_cli._redis.aclose.assert_awaited()
    async_cli._pool.disconnect.assert_awaited()
