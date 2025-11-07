import pytest

from smartutils.error.sys import LibraryUsageError


@pytest.fixture
async def setup_cache(tmp_path_factory):
    yield


@pytest.fixture
async def setup_unreachable_cache(tmp_path_factory):
    config_str = """
redis:
  default:
    host: 222.222.222.222
    port: 6380
    password: ""
    db: 0
    pool_size: 10
    connect_timeout: 10
    socket_timeout: 10
project:
  name: auth
  id: 0
  description: test_auth
  version: 0.0.1
  key: test_key"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.init import init

    init(str(config_file))

    yield


async def test_manager_lock(setup_cache):
    from smartutils.infra import RedisManager

    mgr = RedisManager()
    resource = "pytest:redlock:cover"
    async with mgr.redlock(resource) as lock:
        assert lock
        # 被加锁后可以安全执行写操作; 这里测试能否获取锁
    # 没有异常即为ok


async def test_set_get(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def func():
        cli = redis_mgr.curr
        assert cli is not None
        await cli.set("pytest:curr_cache", "123", ex=1)
        val = await cli.get("pytest:curr_cache")
        assert val == "123"
        await cli._redis.delete("pytest:curr_cache")

    await func()


async def test_out_of_context(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    with pytest.raises(LibraryUsageError):
        redis_mgr.curr


async def test_redis_ping(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()
    assert await redis_mgr.client().ping()


async def test_redis_unreachable_ping(setup_unreachable_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()
    assert not await redis_mgr.client().ping()


async def test_incr_and_decr(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        key = "pytest:cli:incr"
        await cli.delete(key)
        v1 = await cli.incr(key)
        assert int(v1) == 1
        v2 = await cli.incr(key)
        assert int(v2) == 2
        v3 = await cli.decr(key)
        assert int(v3) == 1
        await cli.delete(key)

    await test()


async def test_sadd_srem_scard(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        key = "pytest:cli:set"
        await cli.delete(key)
        await cli.sadd(key, "v1", "v2")
        count = await cli.scard(key)
        assert count == 2
        await cli.srem(key, "v1")
        count2 = await cli.scard(key)
        assert count2 == 1
        await cli.delete(key)

    await test()


async def test_llen(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        key = "pytest:cli:list"
        await cli.delete(key)
        await cli.rpush(key, "a", "b")
        llen = await cli.llen(key)
        assert llen == 2
        await cli.delete(key)

    await test()


async def test_zadd_zrem_zrangebyscore(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        zset = "pytest:cli:zset"
        await cli.delete(zset)
        await cli.zadd(zset, "k1", 10)
        assert await cli.zcard(zset) == 1
        await cli.zadd(zset, "k2", 20)
        assert await cli.zcard(zset) == 2
        members = await cli.zrangebyscore(zset, 0, 30)
        assert "k1" in members and "k2" in members
        await cli.zrem(zset, "k1", "k2")
        members2 = await cli.zrangebyscore(zset, 0, 30)
        assert not members2

    await test()


async def test_safe_rpop_zadd_and_safe_rpush_zrem(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        list_ready = "pytest:cli:list_ready"
        zset_pending = "pytest:cli:zset_pending"
        await cli.delete(list_ready, zset_pending)

        # 先准备任务
        await cli.rpush(list_ready, "task1", "task2")
        # 用 safe_rpop_zadd 弹出一个任务并放入 zset_pending
        async with cli.safe_rpop_zadd(list_ready, zset_pending) as msg:
            assert msg in ("task1", "task2")
            # zset_pending 应该有这个任务
            members = await cli.zrange(zset_pending, 0, -1)
            assert msg in members
        # 弹出后 zset_pending 已被清理
        members2 = await cli.zrange(zset_pending, 0, -1)
        assert msg not in members2

        # 再手动放一个任务到 zset_pending，测试 safe_rpush_zrem
        await cli.zadd_multi(zset_pending, {"task3": 100})
        res = await cli.safe_rpush_zrem(list_ready, zset_pending, "task3")
        assert res == "task3"
        # task3 应该在 list_ready
        vals = await cli.lrange(list_ready, 0, -1)
        assert "task3" in vals
        # task3 应该不在 zset_pending
        members3 = await cli.zrange(zset_pending, 0, -1)
        assert "task3" not in members3

        await cli.delete(list_ready, zset_pending)

    await test()


async def test_real_safe_zpop_zadd_and_safe_zrem_zadd(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        zset_ready = "pytest:cli:zset_ready"
        zset_pending = "pytest:cli:zset_pending2"
        await cli.delete(zset_ready, zset_pending)

        # 准备任务
        await cli.zadd_multi(zset_ready, {"taskA": 1, "taskB": 2})
        # safe_zpop_zadd 应该弹出 score 最小的 taskA
        async with cli.safe_zpop_zadd(zset_ready, zset_pending) as msg:
            assert msg == "taskA"
            # taskA 应该在 pending
            members = await cli.zrange(zset_pending, 0, -1)
            assert "taskA" in members
        # 弹出后 pending 已被清理
        members2 = await cli.zrange(zset_pending, 0, -1)
        assert "taskA" not in members2

        # 再把 taskB 放到 pending，safe_zrem_zadd 归还到 ready
        await cli.zadd_multi(zset_pending, {"taskB": 99})
        res = await cli.safe_zrem_zadd(zset_pending, zset_ready, "taskB", 5)
        assert res == "taskB"
        # taskB 应该在 ready，score 为 5
        ready_members = await cli.zrange(zset_ready, 0, -1, withscores=True)
        found = [x for x in ready_members if x[0] == "taskB" and x[1] == 5.0]
        assert found
        # taskB 应该不在 pending
        pending_members = await cli.zrange(zset_pending, 0, -1)
        assert "taskB" not in pending_members

        await cli.delete(zset_ready, zset_pending)

    await test()


async def test_xadd_xread_xack(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr
        stream = "pytest:cli:stream"
        group = "pytestgroup"
        await cli.delete(stream)
        await cli.ensure_stream_and_group(stream, group)
        await cli.xadd(stream, {"foo": "bar"})
        # 确保 group 存在
        async with cli.xread_xack(stream, group, count=1) as msg_iter:
            assert msg_iter["foo"] == "bar"  # type: ignore
        await cli.delete(stream)

    await test()


async def test_redis_manager_init_with_none():
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.infra.cache.redis import RedisManager

    with pytest.raises(LibraryUsageError):
        RedisManager(None)


async def test_redis_manager_init_with_empty():
    from smartutils.init import reset_all

    await reset_all()
    from smartutils.infra.cache.redis import RedisManager

    with pytest.raises(Exception):
        RedisManager({})


async def test_async_methods_exception_branches(mocker, setup_cache):
    from smartutils.config.schema.redis import RedisConf
    from smartutils.infra.cache.redis import AsyncRedisCli

    conf = RedisConf(
        host="192.168.1.56",
        port=6379,
        db=10,
        pool_size=10,
        connect_timeout=10,
        socket_timeout=10,
        password="",
    )
    cli = AsyncRedisCli(conf, "pytest-exception")

    # 强制 _redis 某方法抛出异常以测 except 分支
    mocker.patch.object(
        cli._redis, "delete", lambda *a, **k: (_ for _ in ()).throw(Exception("fail"))
    )
    with pytest.raises(Exception):
        await cli.delete("foo")

    # mocker close 分支
    mocker.patch.object(
        cli._redis, "aclose", lambda: (_ for _ in ()).throw(Exception("fail"))
    )
    mocker.patch.object(
        cli._pool, "disconnect", lambda: (_ for _ in ()).throw(Exception("fail"))
    )
    # 不抛出异常，只是走 except 路径
    try:
        await cli.close()
    except Exception:
        ...


# 针对 safe_rpop_zadd 及 xread_xack、safe_zpop_zadd 的 yield None/异常分支


async def test_safe_context_none_branches(setup_cache):
    from smartutils.config.schema.redis import RedisConf
    from smartutils.infra.cache.redis import AsyncRedisCli

    conf = RedisConf(
        host="192.168.1.56",
        port=6379,
        db=10,
        pool_size=10,
        connect_timeout=10,
        socket_timeout=10,
        password="",
    )
    cli = AsyncRedisCli(conf, "pytest-none")
    # safe_rpop_zadd: 没有元素时 yield None
    key1, key2 = "pytest:none:list", "pytest:none:zset"
    await cli.delete(key1, key2)
    async with cli.safe_rpop_zadd(key1, key2) as ret:
        assert ret is None

    # safe_zpop_zadd: 没有元素时 yield None
    await cli.delete(key1, key2)
    async with cli.safe_zpop_zadd(key1, key2) as ret:
        assert ret is None

    # xread_xack 发生异常
    stream, group = "pytest:none:stream", "pytestnonegroup"
    await cli.delete(stream)
    # mocker _redis.xreadgroup 让它抛异常
    orig_xreadgroup = cli._redis.xreadgroup

    async def fail(*a, **k):
        raise Exception("fail")

    cli._redis.xreadgroup = fail
    async with cli.xread_xack(stream, group, count=1) as msg:
        assert msg is None
    cli._redis.xreadgroup = orig_xreadgroup


async def test_bitmap_util(setup_cache):
    """
    真正执行RedisBitmapUtil的端到端测试。
    """

    key = "pytest:bitmap:demo"
    from smartutils.infra.cache.redis import RedisManager

    mgr = RedisManager()

    @mgr.use
    async def biz():
        await mgr.curr.delete(key)
        assert await mgr.curr.bitmap.get_all_set_bits(key) is None

        # 清空，初始应无内容
        await mgr.curr.bitmap.set_bit(key, 3, True)
        await mgr.curr.bitmap.set_bit(key, 6, True)
        ret3 = await mgr.curr.bitmap.get_bit(key, 3)
        ret6 = await mgr.curr.bitmap.get_bit(key, 6)
        ret2 = await mgr.curr.bitmap.get_bit(key, 2)
        assert ret3 is True
        assert ret6 is True
        assert ret2 is False
        bits = await mgr.curr.bitmap.get_all_set_bits(key, max_offset=7)
        assert bits == {3, 6}
        # 关闭一个bit
        await mgr.curr.bitmap.set_bit(key, 6, False)
        bits2 = await mgr.curr.bitmap.get_all_set_bits(key, max_offset=7)
        assert bits2 == {3}
        # 全部关闭
        await mgr.curr.bitmap.set_bit(key, 3, False)
        bits3 = await mgr.curr.bitmap.get_all_set_bits(key, max_offset=7)
        assert bits3 == set() or bits3 is None

        await mgr.curr.bitmap.set_bit(key, 1, True)
        assert await mgr.curr.bitmap.get_all_set_bits(key, max_offset=0) == set()

    await biz()
