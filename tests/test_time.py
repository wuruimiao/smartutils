import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from smartutils import time as mytime


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_format_time_with_tz(tz):
    dt = datetime(2024, 4, 27, 15, 30, 0, tzinfo=tz)
    formatted = mytime.format_time(dt, tz=tz)
    assert formatted == dt.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_format_timestamp_with_tz(tz):
    # 2024-04-27 08:00:00 UTC == 2024-04-27 16:00:00 Asia/Shanghai
    dt = datetime(2024, 4, 27, 8, 0, 0, tzinfo=ZoneInfo("UTC"))
    ts = dt.timestamp()
    formatted = mytime.format_timestamp(int(ts), tz=tz)
    dt_in_tz = dt.astimezone(tz)
    assert formatted == dt_in_tz.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_parse_time_str_and_format_time(tz):
    date_str = "2024-05-01 12:00:00"
    dt = mytime.parse_time_str(date_str, tz=tz)
    assert dt.tzinfo == tz
    assert mytime.format_time(dt, tz=tz) == date_str


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_today_and_yesterday_and_tomorrow(tz):
    today_str = mytime.today(tz)
    today_dt = mytime.get_now(tz)
    assert today_str == today_dt.strftime("%Y-%m-%d")

    yesterday_str = mytime.yesterday(tz)
    yesterday_dt = today_dt - timedelta(days=1)
    assert yesterday_str == yesterday_dt.strftime("%Y-%m-%d")

    tomorrow_str = mytime.tomorrow(tz)
    tomorrow_dt = today_dt + timedelta(days=1)
    assert tomorrow_str == tomorrow_dt.strftime("%Y-%m-%d")


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_week_day_str(tz):
    date = datetime(2024, 4, 28, 0, 0, 0, tzinfo=tz)
    result = mytime.week_day_str(date, tz)
    # 2024-04-28 is Sunday
    assert result == "Sunday"


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_today_remain_sec(tz):
    remain_sec = mytime.today_remain_sec(tz)
    # 必须小于等于86400（一天秒数），大于等于0
    assert 0 <= remain_sec <= 86400


@pytest.mark.parametrize("tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")])
def test_get_timestamp_with_tz(tz):
    dt = datetime(2024, 5, 1, 12, 0, 0, tzinfo=tz)
    timestamp = mytime.get_timestamp(dt)
    # 检查回转
    dt2 = datetime.fromtimestamp(timestamp, tz)
    assert dt2.replace(microsecond=0) == dt.replace(microsecond=0)


def test_get_stamp_after_and_before():
    # 不依赖时区，直接测试逻辑
    now = mytime.get_now_stamp_float()
    after = mytime.get_stamp_after(now, day=1, hour=1)
    before = mytime.get_stamp_before(now, day=1, hour=1)
    assert after - before > 0


def test_pass_and_remain_time():
    early = datetime(2024, 4, 25, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    latest = datetime(2024, 4, 27, 3, 15, 30, tzinfo=ZoneInfo("UTC"))
    d, h, m, s = mytime.get_pass_time(early, latest)
    assert d == 2
    assert h == 3
    assert m == 15
    assert s == 30

    r = mytime.get_remain_time(early, early, day=2, hour=1, minute=10, second=5)
    # 截止时间应为 2天1小时10分5秒后
    assert r == mytime.get_pass_time(early, early + timedelta(days=2, hours=1, minutes=10, seconds=5))
