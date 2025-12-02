import asyncio
import threading
import time

import pytest

from smartutils.call import call_hook, exit_on_fail, recursive_reload


def test_exit_on_fail_calls_os_exit(mocker):
    mock_exit = mocker.patch("os._exit")
    exit_on_fail()
    mock_exit.assert_called_once_with(1)


def test_recursive_reload_not_class():
    with pytest.raises(ValueError) as e:
        recursive_reload(1)
    assert str(e.value) == "1 is not a module"


async def test_call_hook_async():
    results = []

    async def async_hook(x, a=1):
        await asyncio.sleep(0.01)
        results.append(("async", x, a))
        return x * 2

    val = await call_hook(async_hook, 5)
    assert val == 10
    assert results == [("async", 5, 1)]

    val = await call_hook(async_hook, 6, a=2)
    assert val == 12
    assert results == [("async", 5, 1), ("async", 6, 2)]


async def test_call_hook_sync_concurrent():
    results = []
    lock = threading.Lock()

    def sync_hook(x):
        time.sleep(0.05)  # 每个sync函数都sleep 0.05s
        with lock:
            results.append(("sync", x))
        return x + 1

    n = 8
    # 用于检验主循环不中断
    ping_event = asyncio.Event()
    ping_count = 0

    # 用 nonlocal 声明，内函数对该变量的修改会影响到最近一层的外部函数作用域里的同名变量。
    async def main_tasks():
        nonlocal ping_count
        # 启动并发的call_hook
        call_tasks = [call_hook(sync_hook, i) for i in range(n)]

        async def pinger():
            nonlocal ping_count
            while not ping_event.is_set():
                ping_count += 1
                await asyncio.sleep(0.01)  # 主循环不断work

        pinger_task = asyncio.create_task(pinger())
        t0 = time.time()
        rets = await asyncio.gather(*call_tasks)
        ping_event.set()
        await pinger_task
        t1 = time.time()

        return rets, t1 - t0, ping_count

    rets, elapsed, ping_count = await main_tasks()

    # 期望并发耗时远小于串行 8*0.05=0.40s，实际应该~0.05~0.10s
    assert elapsed < 0.25, f"耗时断言失败: {elapsed}s"
    assert sorted(rets) == list(range(1, n + 1))  # pyright: ignore[reportArgumentType]
    # 验证并发下都被调用
    assert set(x for _, x in results) == set(range(n))
    # ping_count需>0（即主循环没卡死），且一般很大（循环数多）
    assert ping_count > 2, "主循环被阻塞！"

    print(f"Sync call并发耗时: {elapsed:.3f}s, 主循环ping次数: {ping_count}")
