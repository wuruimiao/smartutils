import sys

import pytest

from smartutils.app import run_main as run_module
from smartutils.app.const import RunEnv


class DummyUvicorn:
    def __init__(self):
        self.called = {}

    def run(self, *args, **kwargs):
        self.called["args"] = args
        self.called["kwargs"] = kwargs


def test_run_env_and_uvicorn(mocker):
    # patch uvicorn
    dummy = DummyUvicorn()
    mocker.patch.object(run_module, "uvicorn", dummy)
    # patch argparse to set values
    argv_backup = sys.argv
    sys.argv = [
        "prog",
        "--host",
        "1.2.3.4",
        "--port",
        "12345",
        "--reload",
        "--conf",
        "abc.yaml",
        "--app",
        "fastapi",
    ]
    # patch AppKey to a dummy for full injection

    mocker.patch.object(run_module, "load_dotenv", return_value=None)

    run_module.run()

    assert RunEnv.get_conf_path() == "abc.yaml"
    assert dummy.called["kwargs"]["host"] == "1.2.3.4"
    assert dummy.called["kwargs"]["port"] == 12345
    assert dummy.called["kwargs"]["reload"] is True
    assert dummy.called["args"][0].startswith("smartutils.app.main.")
    # 恢复sys.argv
    sys.argv = argv_backup


def test_run_default(mocker):
    dummy = DummyUvicorn()
    mocker.patch.object(run_module, "uvicorn", dummy)
    sys.argv = ["prog"]
    mocker.patch.object(run_module, "load_dotenv", return_value=None)

    run_module.run()
    # host为默认
    assert dummy.called["kwargs"]["host"] == "0.0.0.0"
    assert dummy.called["kwargs"]["port"] == 80
    sys.argv = ["prog"]  # 恢复以避免影响后续


def test_run_invalid_app(mocker):
    # 验证非法的app会触发SystemExit
    mocker.patch.object(run_module, "uvicorn", DummyUvicorn())
    sys.argv = ["prog", "--app", "notavalidapp"]
    mocker.patch.object(run_module, "load_dotenv", return_value=None)
    with pytest.raises(SystemExit):
        run_module.run()
    sys.argv = ["prog"]
