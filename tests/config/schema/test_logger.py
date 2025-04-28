import pytest
from smartutils.config.schema.logger import LoguruConfig
from pydantic import ValidationError


def valid_conf(**kwargs):
    return {
        "level": "INFO",
        "format": "<green>{message}</green>",
        "rotation": "10 MB",
        "retention": "7 days",
        "compression": "zip",
        "enqueue": True,
        **kwargs,
    }


@pytest.fixture(scope='function')
def setup_config(tmp_path):
    log_path = tmp_path / "ok_dir" / "my.log"
    log_path.parent.mkdir(parents=True)
    yield valid_conf(logfile=str(log_path))


def test_valid_config(setup_config):
    conf = LoguruConfig(**setup_config)
    assert conf.level == "INFO"
    assert conf.logfile == str(setup_config["logfile"])
    assert conf.compression == "zip"
    assert conf.format.startswith("<green>")


def test_level_invalid():
    # 非法日志等级
    with pytest.raises(ValidationError) as exc:
        LoguruConfig(level="VERBOSE")
    assert " Input should be 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'" in str(exc.value)


@pytest.mark.parametrize("field", ['format', 'rotation', 'retention'])
def test_emtpy(field, setup_config):
    with pytest.raises(ValidationError) as exc:
        setup_config[field] = ""
        LoguruConfig(**setup_config)
    assert "String should have at least 1 character" in str(exc.value) and field in str(exc.value)


def test_compression_invalid():
    with pytest.raises(ValidationError) as exc:
        LoguruConfig(compression="rar")
    assert "Input should be 'zip', 'gz', 'bz2', 'xz' or 'tar'" in str(exc.value)


def test_logfile_dir_not_exist(tmp_path):
    # logfile 父目录不存在
    log_path = tmp_path / "not_exist_dir" / "my.log"
    # 不创建目录
    with pytest.raises(ValidationError) as exc:
        LoguruConfig(logfile=str(log_path))
    assert "logfile parent dir not exist" in str(exc.value)


def test_logfile_none_ok():
    # logfile 为 None 是允许的
    conf = LoguruConfig(logfile=None)
    assert conf.logfile is None
