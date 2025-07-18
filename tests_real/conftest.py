import os

import pytest


@pytest.fixture(autouse=True, scope="function")
async def ensure_smartutils_init():
    test_conf_path = "tests_real/config.test.yaml"
    assert os.path.exists(
        test_conf_path
    ), f"cp tests_real/config.example.yaml {test_conf_path} , then modify."
    from smartutils.init import reset_all

    await reset_all()

    from smartutils.init import init

    await init(test_conf_path)
    yield
    from smartutils.init import release

    await release()
