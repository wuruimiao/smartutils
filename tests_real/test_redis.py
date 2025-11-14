import pytest

from smartutils.error.sys import LibraryUsageError


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
    connect_timeout: 1
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


async def test_manager_lock():
    from smartutils.infra import RedisManager

    mgr = RedisManager()
    resource = "pytest:redlock:cover"
    async with mgr.redlock(resource) as lock:
        assert lock
        # 被加锁后可以安全执行写操作; 这里测试能否获取锁
    # 没有异常即为ok


async def test_out_of_context():
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()

    with pytest.raises(LibraryUsageError):
        redis_mgr.curr


async def test_redis_ping():
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()
    assert await redis_mgr.client().ping()


async def test_redis_unreachable_ping(setup_unreachable_cache):
    from smartutils.infra import RedisManager

    redis_mgr = RedisManager()
    assert not await redis_mgr.client().ping()


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


async def test_async_methods_exception_branches(
    mocker,
):
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


async def test_safe_context_none_branches():
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
    async with cli.safe_q_list.fetch_task_ctx(key1, key2) as ret:
        assert ret is None

    # safe_zpop_zadd: 没有元素时 yield None
    await cli.delete(key1, key2)
    async with cli.safe_q_list.fetch_task_ctx(key1, key2) as ret:
        assert ret is None

    # xread_xack 发生异常
    stream, group = "pytest:none:stream", "pytestnonegroup"
    await cli.delete(stream)
    # mocker _redis.xreadgroup 让它抛异常
    orig_xreadgroup = cli._redis.xreadgroup

    async def fail(*a, **k):
        raise Exception("fail")

    cli._redis.xreadgroup = fail
    async with cli.safe_q_stream.xread_xack(stream, group, count=1) as msg:
        assert msg is None
    cli._redis.xreadgroup = orig_xreadgroup
