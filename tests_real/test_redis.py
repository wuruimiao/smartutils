import pytest


@pytest.fixture
async def setup_cache(tmp_path_factory):
    config_str = """
redis:
  default:
    host: 127.0.0.1
    port: 6379
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

    from smartutils import init

    await init(str(config_file))

    yield
    from smartutils.infra import RedisManager

    await RedisManager().close()

    from smartutils import reset_all

    await reset_all()


@pytest.fixture
async def setup_unreachable_cache(tmp_path_factory):
    config_str = """
redis:
  default:
    host: 127.0.0.1
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

    from smartutils import init

    await init(str(config_file))

    yield
    from smartutils.infra import RedisManager

    await RedisManager().close()

    from smartutils import reset_all

    await reset_all()


async def test_set_get(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def func():
        cli = redis_mgr.curr()
        assert cli is not None
        await cli.set("pytest:curr_cache", "123", expire=1)
        val = await cli.get("pytest:curr_cache")
        assert val == "123"
        await cli._redis.delete("pytest:curr_cache")

    await func()


async def test_out_of_context(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    with pytest.raises(RuntimeError):
        redis_mgr.curr()


async def test_ping(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()
    assert await redis_mgr.client().ping()


async def test_unreachable_ping(setup_unreachable_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()
    assert not await redis_mgr.client().ping()


async def test_incr_and_decr(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr()
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
        cli = redis_mgr.curr()
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
        cli = redis_mgr.curr()
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
        cli = redis_mgr.curr()
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
        cli = redis_mgr.curr()
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


async def test_safe_zpop_zadd_and_safe_zrem_zadd(setup_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    @redis_mgr.use()
    async def test():
        cli = redis_mgr.curr()
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
        cli = redis_mgr.curr()
        stream = "pytest:cli:stream"
        group = "pytestgroup"
        await cli.delete(stream)
        await cli.ensure_stream_and_group(stream, group)
        msgid = await cli.xadd(stream, {"foo": "bar"})
        # 确保 group 存在
        async with cli.xread_xack(stream, group, count=1) as msg_iter:
            assert msg_iter["foo"] == "bar"
        await cli.delete(stream)

    await test()
