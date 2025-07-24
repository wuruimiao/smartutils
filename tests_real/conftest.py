import os
import sys
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope="function")
async def ensure_smartutils_init():
    stub_path = Path(__file__).parent / "grpcbin" / "stub"
    assert stub_path.exists(), "stub path does not exist."
    if str(stub_path) not in sys.path:
        sys.path.insert(0, str(stub_path))

    test_conf_path = "tests_real/config.test.yaml"
    assert os.path.exists(
        test_conf_path
    ), f"cp tests_real/config.example.yaml {test_conf_path} , then modify."
    from smartutils.init import reset_all

    await reset_all()

    from smartutils.init import init

    init(test_conf_path)
    yield
    from smartutils.init import release

    await release()
