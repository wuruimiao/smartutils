import os

from smartutils.file import _lock


def test_lock_basic_and_cleanup(tmp_path):
    lock_dir = tmp_path
    lock = _lock.Lock(lock_dir)
    # _file_name 创建
    assert os.path.exists(lock._file_name)
    # 调用基本方法无异常
    lock.lock()
    lock.unlock()
    # __del__能正常关闭
    del lock


def test_lock_write_and_read_lock(tmp_path):
    lock = _lock.Lock(tmp_path)
    # read_lock上下文
    with lock.read_lock():
        assert os.path.exists(lock._file_name)
    # write_lock上下文
    with lock.write_lock():
        # _record会写pid和thread ident
        pass


def test_lock_del_ioerror(tmp_path, mocker):
    lock = _lock.Lock(tmp_path)
    mocker.patch.object(
        lock._fd, "close", lambda: (_ for _ in ()).throw(IOError("test"))
    )
    # 日志不会崩溃，仅记录错误
    lock.__del__()
