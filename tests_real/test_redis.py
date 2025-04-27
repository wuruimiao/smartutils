import pytest


@pytest.fixture(scope="session", autouse=True)
async def setup_cache(tmp_path_factory):
    config_str = """
redis:
  host: 192.168.1.56
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

    from smartutils.config import init
    init(str(config_file))
    print(config_file)

    from smartutils.cache import init
    init()
    yield
    from smartutils.cache import cache
    await cache.close()


@pytest.mark.asyncio
async def test_curr_cache_in_context():
    from smartutils.cache import cache

    @cache.with_cache
    async def func():
        cli = cache.curr_cache()
        assert cli is not None
        await cli.set("pytest:curr_cache", "123", expire=1)
        val = await cli.get("pytest:curr_cache")
        assert val == "123"
        await cli._redis.delete("pytest:curr_cache")

    await func()


@pytest.mark.asyncio
async def test_curr_cache_out_of_context():
    from smartutils.cache import cache

    cli = cache.curr_cache()
    assert cli is None
