import pytest


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    from smartutils.design.singleton import reset_all
    reset_all()
