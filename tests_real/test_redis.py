import pytest


@pytest.fixture(scope='function', autouse=True)
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
    socket_timeout: 10"""
    tmp_dir = tmp_path_factory.mktemp("config")
    config_file = tmp_dir / "test_config.yaml"
    with open(config_file, "w") as f:
        f.write(config_str)

    from smartutils import init_all
    await init_all(str(config_file))

    yield
    from smartutils.infra import RedisManager
    await RedisManager().close()

    from smartutils import reset_all
    reset_all()


@pytest.mark.asyncio
async def test_curr_cache_in_context():
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


@pytest.mark.asyncio
async def test_curr_cache_out_of_context():
    from smartutils.infra import RedisManager
    redis_mgr = RedisManager()

    with pytest.raises(RuntimeError):
        redis_mgr.curr()
