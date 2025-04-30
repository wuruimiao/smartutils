import pytest


@pytest.fixture(autouse=True)
async def cleanup():
    yield

    from smartutils import release
    await release()
