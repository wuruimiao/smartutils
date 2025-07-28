from smartutils.app.const import HeaderKey
from smartutils.app.plugin.common import CustomHeader


class DummyAdapter:
    def __init__(self):
        self.headers = {}

    def set_header(self, key, value):
        self.headers[key] = value

    def get_header(self, key):
        return self.headers.get(key)


def test_permission_user_ids_set_and_get():
    adapter = DummyAdapter()

    # set user ids
    ids = [123, 456, 789]
    CustomHeader.permission_user_ids(adapter, value=ids, set_value=True)  # type: ignore
    assert adapter.headers[HeaderKey.X_P_USER_IDS] == "123,456,789"

    # get user ids
    res = CustomHeader.permission_user_ids(adapter)  # type: ignore
    assert res == [123, 456, 789]


def test_permission_user_ids_none():
    adapter = DummyAdapter()
    # 没有设置任何 header，返回 None
    assert CustomHeader.permission_user_ids(adapter) is None  # type: ignore


def test_permission_user_ids_non_str(mocker):
    adapter = DummyAdapter()
    adapter.set_header(HeaderKey.X_P_USER_IDS, 100)  # 故意用非字符串类型
    # mocker 替换 logger
    mocker.patch("smartutils.app.plugin.common.logger")
    assert CustomHeader.permission_user_ids(adapter) is None  # type: ignore


def test_permission_user_ids_empty():
    adapter = DummyAdapter()
    adapter.set_header(HeaderKey.X_P_USER_IDS, "")
    assert CustomHeader.permission_user_ids(adapter) is None  # type: ignore
