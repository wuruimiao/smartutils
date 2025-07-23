import builtins

import pytest

import smartutils.system.cgroup as cgroupmod


def test_init_psutil_not_installed(mocker):
    mocker.patch.object(cgroupmod, "psutil", None)
    with pytest.raises(AssertionError):
        cgroupmod.IOController("test", ["8:0"], ["cmd"])


def make_controller(tmp_path, mocker):
    # 假定psutil已可用
    mocker.patch.object(cgroupmod, "psutil", object())
    ctl = cgroupmod.IOController(
        name="test",
        devices=["8:0"],
        command_names=["foo"],
        rbps=100,
        wbps=200,
        riops=1,
        wiops=2,
        cgroup_version="v2",
    )
    return ctl, mocker


def test_create_cgroup_enable_io_controller(tmp_path, mocker):
    cgroup_dir = tmp_path / "test"
    # fake cgroup directory
    (cgroup_dir).mkdir(parents=True)
    ctl = cgroupmod.IOController("test", ["8:0"], ["cmd"])
    ctl._dir = str(cgroup_dir)
    mocker.patch.object(cgroupmod, "psutil", True)
    # io controller write
    ctrl_file = cgroup_dir / "cgroup.controllers"
    ctrl_file.write_text("io")
    ctl.create_cgroup()  # exist_ok,分支覆盖
    assert ctrl_file.exists()


def test_create_cgroup_invalid_version(mocker):
    ctl = cgroupmod.IOController("test", ["8:0"], ["cmd"], cgroup_version="foo")
    mocker.patch.object(cgroupmod, "psutil", True)
    # mock 掉 makedirs，防止系统目录写导致 OSError
    mocker.patch("os.makedirs", return_value=None)
    with pytest.raises(ValueError):
        ctl.create_cgroup()
    ctl = cgroupmod.IOController("test", ["8:0"], ["cmd"], cgroup_version="foo")
    mocker.patch.object(cgroupmod, "psutil", True)
    with pytest.raises(ValueError):
        ctl.create_cgroup()


def test_set_io_limits_v2(tmp_path, mocker):
    cgroup_dir = tmp_path / "io"
    cgroup_dir.mkdir()
    ctl = cgroupmod.IOController(
        "io", ["8:1"], ["cmd"], rbps=111, wbps=222, cgroup_version="v2"
    )
    ctl._dir = str(cgroup_dir)
    mocker.patch.object(cgroupmod, "psutil", True)
    io_max = cgroup_dir / "io.max"
    io_max.touch()
    ctl.set_io_limits()
    assert io_max.exists()


def test_set_io_limits_v1(tmp_path, mocker):
    cgroup_dir = tmp_path / "blkio"
    cgroup_dir.mkdir()
    ctl = cgroupmod.IOController(
        "blkio", ["8:1"], ["c"], rbps=333, wbps=444, cgroup_version="v1"
    )
    ctl._dir = str(cgroup_dir)
    mocker.patch.object(cgroupmod, "psutil", True)
    rfile = cgroup_dir / "blkio.throttle.read_bps_device"
    wfile = cgroup_dir / "blkio.throttle.write_bps_device"
    rfile.touch()
    wfile.touch()
    ctl.set_io_limits()
    assert rfile.exists() and wfile.exists()


def test_set_io_limits_version_wrong(mocker):
    ctl = cgroupmod.IOController("test", ["8:0"], ["c"], cgroup_version="foo")
    mocker.patch.object(cgroupmod, "psutil", True)
    with pytest.raises(ValueError):
        ctl.set_io_limits()


def test_add_remove_process_to_cgroup(tmp_path, mocker):
    # 构造 controller
    cgroup_dir = tmp_path / "cgroupv2"
    cgroup_dir.mkdir()
    ctl = cgroupmod.IOController("cgroupv2", ["8:1"], ["foo"], cgroup_version="v2")
    ctl._dir = str(cgroup_dir)
    mocker.patch.object(cgroupmod, "psutil", True)
    # 测试 add
    procs_file = cgroup_dir / "cgroup.procs"
    procs_file.write_text("")
    ctl.add_process_to_cgroup(1234)
    out = procs_file.read_text()
    assert "1234" in out

    # 测试 remove，有 pid
    procs_file.write_text("1234\n5678\n")
    ctl.remove_process_from_cgroup(1234)
    # 判断目标pid确实被移除，其它行保留，无论行末多少换行都不是问题
    out = procs_file.read_text()
    assert "1234" not in out  # 保证被移除了
    assert "5678" in out  # 其它pid应保留

    # 测试 remove，无 pid分支（全清空）
    procs_file.write_text("1234\n")
    ctl.remove_process_from_cgroup()
    assert procs_file.read_text() == ""


def test_add_process_to_cgroup_processlookup(mocker, tmp_path):
    cgroup_dir = tmp_path / "cg"
    cgroup_dir.mkdir()
    ctl = cgroupmod.IOController("cg", ["8:0"], ["foo"])
    ctl._dir = str(cgroup_dir)
    procs_file = cgroup_dir / "cgroup.procs"
    procs_file.touch()

    class DummyLogger:
        def error(self, msg):  # 符合logger接口
            self.msg = msg

    dummy_logger = DummyLogger()
    mocker.patch.object(cgroupmod, "logger", dummy_logger)
    orig_open = builtins.open

    def fail_open(*args, **kwargs):
        raise ProcessLookupError("fail")

    mocker.patch.object(builtins, "open", fail_open)
    ctl.add_process_to_cgroup(123)  # 捕获异常分支
    mocker.patch.object(builtins, "open", orig_open)
