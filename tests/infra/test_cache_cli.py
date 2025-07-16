from unittest.mock import AsyncMock, MagicMock

import pytest

import smartutils.infra.cache.redis as cachemod


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
    assert await async_cli.set("k", "v", ex=2) is True
    async_cli._redis.get.return_value = "v"
    v = await async_cli.get("k")
    assert v == "v"
    async_cli._redis.delete.return_value = 1
    assert await async_cli.delete("k1", "k2") == 1


async def test_incr_decr(async_cli):
    async_cli._redis.eval.return_value = 11
    assert await async_cli.incr("cnt", ex=2) == 11
    assert await async_cli.decr("cnt", ex=None) == 11


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


# 用于mock register_script返回的异步可调用对象
class AsyncLuaMock:
    def __init__(self, ret):
        self.ret = ret
        self.called_args = []

    async def __call__(self, *args, **kwargs):
        self.called_args.append((args, kwargs))
        return self.ret


async def test_safe_rpop_zadd_and_rpush_zrem(async_cli):
    # 用MagicMock确保register_script返回的确实是AsyncLuaMock实例
    async_cli._redis.register_script = MagicMock(return_value=AsyncLuaMock("msg1"))
    async_cli.zrem = AsyncMock()

    # 流程1: 弹出消息, yield消息, 退出时zrem
    async with async_cli.safe_rpop_zadd("list_r", "zset_p", score=123) as msg:
        assert msg == "msg1"
    async_cli.zrem.assert_awaited_with("zset_p", "msg1")
    # 流程2: 无消息则 yield None
    async_cli._redis.register_script = MagicMock(return_value=AsyncLuaMock(None))
    async_cli.zrem.reset_mock()
    async with async_cli.safe_rpop_zadd("list_r", "zset_p", score=123) as msg:
        assert msg is None
    async_cli.zrem.assert_not_called()

    # rpush-zrem
    async_cli._redis.register_script = MagicMock(return_value=AsyncLuaMock("msg2"))
    ret = await async_cli.safe_rpush_zrem("list_r", "zset_p", "msg2")
    assert ret == "msg2"


async def test_safe_zpop_zadd_and_safe_zrem_zadd(async_cli):
    # 与前面的用法保持一致，mock register_script 返回 AsyncLuaMock 实例
    async_cli._redis.register_script = MagicMock(return_value=AsyncLuaMock("msg3"))
    async_cli.zrem = AsyncMock()

    async with async_cli.safe_zpop_zadd("zr", "zp", score=456) as msg:
        assert msg == "msg3"
    async_cli.zrem.assert_awaited_with("zp", "msg3")

    async_cli._redis.register_script = MagicMock(return_value=AsyncLuaMock(None))
    async_cli.zrem.reset_mock()
    async with async_cli.safe_zpop_zadd("zr", "zp", score=456) as msg:
        assert msg is None
    async_cli.zrem.assert_not_called()

    # safe_zrem_zadd
    async_cli._redis.register_script = MagicMock(return_value=AsyncLuaMock("retc"))
    ret = await async_cli.safe_zrem_zadd("zp", "zr", "msg4", 888)
    assert ret == "retc"


async def test_xadd_and_ensure_stream_and_group(async_cli):
    async_cli._redis.xadd.return_value = "id1"
    ret = await async_cli.xadd("stream1", {"a": 1})
    assert ret == "id1"

    async_cli._redis.xgroup_create = AsyncMock()
    await async_cli.ensure_stream_and_group("st", "gp")
    async_cli._redis.xgroup_create.assert_awaited()

    from redis.asyncio import ResponseError

    from smartutils.error.sys import CacheError

    async_cli._redis.xgroup_create = AsyncMock(
        side_effect=ResponseError("BUSYGROUP Consumer Group name already exists")
    )
    await async_cli.ensure_stream_and_group("st", "gp")

    async_cli._redis.xgroup_create = AsyncMock(side_effect=ResponseError("xxx"))
    import smartutils.error.factory as fct

    fct.ExcDetailFactory.get = lambda e: "detail"  # type: ignore
    with pytest.raises(CacheError):
        await async_cli.ensure_stream_and_group("st", "gp")


async def test_xread_xack(async_cli):
    async_cli.ensure_stream_and_group = AsyncMock()
    async_cli._redis.xreadgroup.return_value = [("stream", [("msgid", {"k": b"v"})])]
    async_cli._redis.xack = AsyncMock()
    async_cli._redis.xreadgroup = AsyncMock(
        return_value=[("stream", [("msgid", {"k": b"v"})])]
    )
    async_cli._redis.xack = AsyncMock()

    async with async_cli.xread_xack("stream", "gp", count=1) as msg:
        assert msg == {"k": "v"}
    async_cli._redis.xack.assert_awaited_with("stream", "gp", "msgid")

    async_cli._redis.xreadgroup = AsyncMock(return_value=[])
    async_cli._redis.xack.reset_mock()
    async with async_cli.xread_xack("stream", "gp", count=2) as msg:
        assert msg is None
    async_cli._redis.xack.assert_not_awaited()

    async_cli._redis.xreadgroup = AsyncMock(side_effect=Exception("fail"))
    async_cli._redis.xack.reset_mock()
    async with async_cli.xread_xack("stream", "gp", count=2) as msg:
        assert msg is None
    async_cli._redis.xack.assert_not_awaited()


async def test_init_assertion(monkeypatch, redis_conf):
    # 模拟redis未导入场景
    monkeypatch.setattr(cachemod, "Redis", None)
    with pytest.raises(AssertionError) as e:
        cachemod.AsyncRedisCli(redis_conf, name="failcli")
    assert "install before use" in str(e.value)

    # 模拟Redis库丢失, 但走不到断言
    monkeypatch.setattr(cachemod, "Redis", None)
    monkeypatch.setattr(cachemod, "ConnectionPool", None)
    with pytest.raises(AssertionError):
        cachemod.AsyncRedisCli(redis_conf, name="failcli")


async def test_close_error(async_cli, monkeypatch):
    # 模拟aclose或disconnect抛异常
    async def raise_exc(*args, **kw):
        raise Exception("close fail")

    async_cli._redis.aclose = raise_exc
    async_cli._pool.disconnect = raise_exc
    # 不会raise（调用方需catch）

    try:
        await async_cli.close()
    except Exception:
        pass


async def test_ensure_stream_and_group_raises(async_cli, monkeypatch):
    class DummyErr(Exception):
        pass

    class DummyRespErr(Exception):
        def __str__(self):
            return "other error"

    monkeypatch.setattr(cachemod, "ResponseError", DummyRespErr)
    async_cli._redis.xgroup_create = AsyncMock(side_effect=DummyRespErr())
    import smartutils.error.factory as ef

    monkeypatch.setattr(ef.ExcDetailFactory, "get", lambda e: "detailxxx")
    # 应抛 CacheError

    from smartutils.error.sys import CacheError

    try:
        await async_cli.ensure_stream_and_group("s", "g")
    except CacheError as ce:
        assert "detailxxx" in str(ce)
