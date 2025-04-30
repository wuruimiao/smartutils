import pytest


# 自动应用到所有测试函数
@pytest.fixture(autouse=True)
async def cleanup():
    yield

    from smartutils import release

    await release()
