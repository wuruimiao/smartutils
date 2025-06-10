import asyncio

import pytest

from smartutils.init import reset_all


@pytest.fixture(autouse=True, scope="function")
async def ensure_smartutils_init():
    await reset_all()
    yield
