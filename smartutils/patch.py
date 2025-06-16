from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch


@contextmanager
def patched_manager_with_mocked_dbcli(patch_target):
    """
    通用patch Manager依赖db client的上下文管理器。
    用法：
        with patched_manager_with_mocked_dbcli() as (MockDBCli, fake_session, instance):
            # ...测试体...
    """
    with patch(patch_target) as MockDBCli:
        fake_session = AsyncMock()
        fake_session.commit = AsyncMock()
        fake_session.rollback = AsyncMock()
        fake_session.in_transaction = MagicMock(return_value=True)

        async_context_mgr = AsyncMock()
        # 这里由仅 fake_session -> (fake_session, None)
        async_context_mgr.__aenter__.return_value = (fake_session, None)
        async_context_mgr.__aexit__.return_value = None

        instance = MockDBCli.return_value
        instance.db.return_value = async_context_mgr
        instance.close = AsyncMock()

        yield MockDBCli, fake_session, instance
