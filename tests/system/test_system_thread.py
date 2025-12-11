import threading

from smartutils.system import thread


def test_is_main_thread_true():
    """
    测试主线程内 is_main_thread 返回 True
    """
    assert thread.is_main_thread() is True
    assert thread.is_multithreaded() is False


def run_and_return(f):
    res = []

    def target():
        res.append(f())

    t = threading.Thread(target=target)
    t.start()
    t.join()
    return res[0]


def test_is_main_thread_false_subthread():
    """
    在子线程中 is_main_thread 应返回 False
    """
    assert run_and_return(thread.is_main_thread) is False


def test_is_multithreaded_main_only(mocker):
    """
    mock 只有主线程, active_count 返回1
    """
    mocker.patch("threading.active_count", return_value=1)
    assert thread.is_multithreaded() is False


def test_is_multithreaded_has_thread(mocker):
    """
    mock 有多个线程, active_count 返回2
    """
    mocker.patch("threading.active_count", return_value=2)
    assert thread.is_multithreaded() is True


def test_is_multithreaded_real_thread():
    """
    真正起子线程，主线程和子线程都调用 is_multithreaded，active_count 应都大于1
    """
    ready = threading.Event()
    done = threading.Event()
    subthread_result = []

    def worker():
        ready.set()
        subthread_result.append(thread.is_multithreaded())
        done.wait()

    t = threading.Thread(target=worker)
    t.start()
    ready.wait()
    try:
        assert thread.is_main_thread() is True
        assert thread.is_multithreaded() is True
        assert subthread_result[0] is True
    finally:
        done.set()
        t.join()
