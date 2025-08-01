import subprocess
import sys
import time

import pytest

from smartutils.system import process


def test_cur_pid(mocker):
    mocker.patch.object(process.os, "getpid", return_value=1)
    assert process.cur_pid() == 1


def test_cur_tid():
    tid = process.cur_tid()
    # threading.currentThread().ident 必定不为 None
    import threading

    assert tid == threading.currentThread().ident
    assert isinstance(tid, int)


def test_get_host_ip(monkeypatch):
    # mock socket，返回一个假IP
    class DummySocket:
        def connect(self, addr): ...

        def getsockname(self):
            return ("123.123.123.123", 12345)

        def close(self): ...

    monkeypatch.setattr("socket.socket", lambda *a, **kw: DummySocket())
    ip = process.get_host_ip()
    assert ip == "123.123.123.123"


def test_import_by_name():
    assert process.import_by_name("sys") is sys


def test_run_cmd_success(monkeypatch):
    def dummy_check_output(cmd, **kwargs):
        return "hello\n"

    monkeypatch.setattr("subprocess.check_output", dummy_check_output)
    out, ok = process.run_cmd(["echo", "hi"])
    assert ok and "hello" in out


def test_run_cmd_calledprocesserror(monkeypatch):
    class DummyError(Exception):
        output = "err"

    def raise_exc(cmd, **a):
        raise subprocess.CalledProcessError(1, cmd, "err")

    monkeypatch.setattr("subprocess.check_output", raise_exc)
    out, ok = process.run_cmd(["notexist"])
    assert not ok and "err" in out


def test_run_cmd_file_not_found(monkeypatch):
    def raise_exc(cmd, **a):
        raise FileNotFoundError("missing!")

    monkeypatch.setattr("subprocess.check_output", raise_exc)
    out, ok = process.run_cmd(["notexist"])
    assert not ok and "missing!" in out


def test_run_cmd_timeout(monkeypatch):
    def raise_exc(cmd, **a):
        raise subprocess.TimeoutExpired(cmd, 1)

    monkeypatch.setattr("subprocess.check_output", raise_exc)
    out, ok = process.run_cmd(["toolong"])
    assert not ok


def test_sleep(monkeypatch):
    called = []
    monkeypatch.setattr(time, "sleep", lambda x: called.append(x))
    process.sleep(3, at_least=2)
    assert called and all(2 <= x <= 3 for x in called)


def test_sleep_at_least_computation(mocker):
    # 监控 random.randint 的调用参数
    patcher = mocker.patch.object(process.random, "randint", return_value=1)
    sec = 9
    expected_at_least = max(sec - 2 * sec // 3, 1)
    process.sleep(sec)
    patcher.assert_called_with(expected_at_least, sec)


def test_stoppable_thread_stop_and_stopped():
    t = process.StoppableThread()
    assert not t.stopped()
    t.stop()
    assert t.stopped()


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="multiprocessing kill not safe in win test"
)
def test_run_with_timeout_normal(monkeypatch):
    # mock subprocess.run
    class DummyResult:
        def __init__(self):
            self.stdout, self.stderr, self.returncode = "out", "err", 0

    monkeypatch.setattr("subprocess.run", lambda *a, **k: DummyResult())
    out1, out2, err = process.run_with_timeout(["echo"], 1)
    assert out1 == "out" and out2 == "err" and err.code == 0


@pytest.mark.skipif(
    sys.platform.startswith("win"), reason="multiprocessing kill not safe in win test"
)
def test_run_with_timeout_timeout(mocker):
    # mock multiprocessing.Process
    class DummyProc:
        def __init__(self):
            self._alive = True
            self.pid = 88888

        def start(self): ...

        def join(self, timeout=None):
            time.sleep(0.01)

        def is_alive(self):
            return self._alive

        def terminate(self):
            self._alive = False

    dummy_proc_instance = DummyProc()
    mocker.patch("multiprocessing.Process", return_value=dummy_proc_instance)
    mocker.patch("multiprocessing.Queue", return_value=mocker.MagicMock())

    # mock is_linux/is_win 平台分支
    mocker.patch.object(process, "is_linux", return_value=True)
    mocker.patch.object(process, "is_win", return_value=False)
    # mock killpg 和 setpgrp（防止杀死 pytest 自身）
    mocker.patch("os.killpg", return_value=None)
    mocker.patch("os.setpgrp", return_value=None)
    # mock signal.SIGTERM
    mocker.patch("signal.SIGTERM", 15, create=True)

    out1, out2, err = process.run_with_timeout(["sleep", "2"], timeout=0.01)

    # 超时后应返回 TimeOutError 或 out2=="超时"
    assert (hasattr(err, "code") and err.code != 0) or out2 == "超时"
