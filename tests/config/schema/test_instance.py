import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from smartutils.config.schema.instance import InstanceConf

def aware_dt():
    # 返回带时区的 datetime
    return datetime(2025, 5, 7, 10, 0, 0, tzinfo=timezone(timedelta(hours=8)))

def naive_dt():
    # 返回不带时区的 datetime
    return datetime(2025, 5, 7, 10, 0, 0)

def test_instance_conf_valid():
    conf = InstanceConf(id=1, release_time=aware_dt())
    assert conf.id == 1
    assert conf.release_time == aware_dt()
    # 检查 release_timestamp_ms
    assert conf.release_timestamp_ms == int(conf.release_time.timestamp()) * 1000
    # 检查 kw 属性
    assert conf.kw == {"instance": 1, "epoch": conf.release_timestamp_ms}

def test_instance_conf_release_time_must_be_aware():
    # 不带时区应报错
    with pytest.raises(ValidationError) as exc:
        InstanceConf(id=1, release_time=naive_dt())
    assert "release_time must be an aware datetime" in str(exc.value)