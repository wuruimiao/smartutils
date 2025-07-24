import pytest


# 作用域是conftest同目录下的所有测试用例
# autouse=True: 让这个 fixture 自动应用于作用域内的所有测试用例，无需手动在函数里写
# scope="function": 指定此 fixture 的作用范围是“函数级别”，即每一个测试函数（包括方法）都会独立调用一次这个 fixture；用完就 teardown 下一个函数重新 setup。
@pytest.fixture(autouse=True, scope="function")
async def ensure_smartutils_init():
    from smartutils.init import reset_all

    await reset_all()
    yield
    from smartutils.init import release

    await release()
