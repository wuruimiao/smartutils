import pytest
from smartutils.log import logger


@pytest.fixture(autouse=True)
def cleanup_loguru():
    yield
    logger.remove()
