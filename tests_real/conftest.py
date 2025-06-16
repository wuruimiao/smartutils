import pytest


@pytest.fixture(autouse=True, scope="function")
async def ensure_smartutils_init():
    from smartutils.init import reset_all

    await reset_all()

    from smartutils.init import init

    await init("tests_real/config.test.yaml")
    yield
    from smartutils.infra.init import release

    await release()
