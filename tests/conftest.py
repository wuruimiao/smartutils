import pytest


@pytest.fixture(autouse=True, scope="function")
async def ensure_smartutils_init():
    from smartutils.init import reset_all

    await reset_all()
    yield
    from smartutils.init import release

    await release()
