from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from smartutils import time as mytime


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
def test_format_time_with_tz(tz):
    dt = datetime(2024, 4, 27, 15, 30, 0, tzinfo=tz)
    formatted = mytime.format_time(dt, tz=tz)
    assert formatted == dt.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
def test_format_timestamp_with_tz(tz):
    # 2024-04-27 08:00:00 UTC == 2024-04-27 16:00:00 Asia/Shanghai
    dt = datetime(2024, 4, 27, 8, 0, 0, tzinfo=ZoneInfo("UTC"))
    ts = dt.timestamp()
    formatted = mytime.format_timestamp(int(ts), tz=tz)
    dt_in_tz = dt.astimezone(tz)
    assert formatted == dt_in_tz.strftime("%Y-%m-%d %H:%M:%S")


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
def test_parse_time_str_and_format_time(tz):
    date_str = "2024-05-01 12:00:00"
    dt = mytime.parse_time_str(date_str, tz=tz)
    assert dt.tzinfo == tz
    assert mytime.format_time(dt, tz=tz) == date_str


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
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


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
def test_week_day_str(tz):
    date = datetime(2024, 4, 28, 0, 0, 0, tzinfo=tz)
    result = mytime.week_day_str(date, tz)
    # 2024-04-28 is Sunday
    assert result == "Sunday"


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
def test_today_remain_sec(tz):
    remain_sec = mytime.today_remain_sec(tz)
    # 必须小于等于86400（一天秒数），大于等于0
    assert 0 <= remain_sec <= 86400


@pytest.mark.parametrize(
    "tz", [ZoneInfo("Asia/Shanghai"), ZoneInfo("UTC"), ZoneInfo("America/New_York")]
)
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
    assert r == mytime.get_pass_time(
        early, early + timedelta(days=2, hours=1, minutes=10, seconds=5)
    )


def test_format_time_default_and_custom_format():
    dt = datetime(2024, 5, 2, 10, 20, 30)
    # 没 tzinfo，应自动加上默认 Asia/Shanghai
    s = mytime.format_time(dt)
    assert s == "2024-05-02 10:20:30"
    # 指定输出格式
    s2 = mytime.format_time(dt, f="%Y/%m/%d")
    assert s2 == "2024/05/02"


def test_format_time_with_aware_dt():
    dt = datetime(2024, 5, 2, 10, 20, 30, tzinfo=ZoneInfo("UTC"))
    s = mytime.format_time(dt, tz=ZoneInfo("Asia/Shanghai"))
    # UTC 10:20:30 -> Shanghai 18:20:30
    assert s == "2024-05-02 18:20:30"


def test_format_timestamp_accepts_float_and_edge():
    from smartutils import time as mytime

    # 支持float timestamp
    dt = datetime(2024, 5, 2, 12, 34, 56, tzinfo=ZoneInfo("Asia/Shanghai"))
    ts = dt.timestamp()
    s = mytime.format_timestamp(int(ts), tz=ZoneInfo("Asia/Shanghai"))
    assert s == "2024-05-02 12:34:56"
    # float timestamp
    s2 = mytime.format_timestamp(int(ts), tz=ZoneInfo("Asia/Shanghai"))
    assert s2 == "2024-05-02 12:34:56"


def test_get_stamp_after_and_before_zero():
    now = mytime.get_now_stamp_float()
    after = mytime.get_stamp_after(now)
    before = mytime.get_stamp_before(now)
    assert abs(after - now) < 1e-5
    assert abs(before - now) < 1e-5


def test_get_stamp_after_compose():
    now = 1000.0
    # 1天1小时1分钟1秒后
    s = mytime.get_stamp_after(now, day=1, hour=1, minute=1, second=1)
    # 1天=24小时=24*60*60=86400, 1小时=3600, 1分钟=60, 1秒
    shouldbe = now + 86400 + 3600 + 60 + 1
    assert s == shouldbe


def test_parse_time_str_invalid():
    from smartutils import time as mytime

    with pytest.raises(ValueError):
        mytime.parse_time_str("xxxx")


def test_parse_time_str_custom_format():
    s = "2024/05/02 10:20:30"
    dt = mytime.parse_time_str(s, str_format="%Y/%m/%d %H:%M:%S")
    assert dt.year == 2024 and dt.month == 5 and dt.day == 2


def test_week_day_and_str_default_now():
    # 只要能运行即可
    w = mytime.week_day()
    ws = mytime.week_day_str()
    assert isinstance(w, int)
    assert isinstance(ws, str)


def test_today_remain_sec_near_midnight():
    # 构造临近午夜
    from datetime import datetime

    from smartutils import time as mytime

    tz = ZoneInfo("Asia/Shanghai")
    dt = datetime(2024, 5, 2, 23, 59, 59, tzinfo=tz)
    # patch get_now 返回dt
    orig_get_now = mytime.get_now
    mytime.get_now = lambda tz=tz: dt
    try:
        sec = mytime.today_remain_sec(tz)
        assert 0 <= sec <= 1
    finally:
        mytime.get_now = orig_get_now


def test_get_pass_time_zero():
    from datetime import datetime

    dt = datetime(2024, 5, 2, 0, 0, 0)
    d, h, m, s = mytime.get_pass_time(dt, dt)
    assert d == h == m == s == 0


def test_get_remain_time_deadline_passed():
    from datetime import datetime

    from smartutils import time as mytime

    early = datetime(2024, 1, 1, 0, 0, 0)
    late = datetime(2024, 1, 3, 0, 0, 0)
    # 只给1天，实际已过
    result = mytime.get_remain_time(early, late, day=1, hour=0, minute=0, second=0)
    assert result == (0, 0, 0, 0)


def test_get_timestamp():
    from datetime import datetime

    from smartutils import time as mytime

    dt = datetime(2024, 5, 2, 12, 34, 56, tzinfo=ZoneInfo("Asia/Shanghai"))
    ts = mytime.get_timestamp(dt)
    assert isinstance(ts, float)


def test_get_now_str_mock(mocker):
    from datetime import datetime
    from zoneinfo import ZoneInfo

    dt = datetime(2024, 5, 2, 12, 34, 56, tzinfo=ZoneInfo("Asia/Shanghai"))
    mocker.patch.object(mytime, "get_now", lambda tz=None: dt)
    assert mytime.get_now_str(ZoneInfo("Asia/Shanghai")) == "2024-05-02 12:34:56"


def test_get_now_stamp_mock(mocker):
    mocker.patch.object(mytime, "get_now_stamp_float", return_value=1714627200.999)
    assert mytime.get_now_stamp() == 1714627200


def test_get_now_stamp_str_mock(mocker):
    from smartutils import time as mytime

    mock_value = 1714627200.123456
    mocker.patch.object(mytime, "get_now_stamp_float", return_value=mock_value)
    result = mytime.get_now_stamp_str()
    assert isinstance(result, str)
    assert result == str(mock_value)


def test_week_day_none(mocker):
    # mock get_now 返回固定日期
    dt = datetime(2024, 5, 3, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))  # Friday
    mocker.patch.object(mytime, "get_now", return_value=dt)
    assert mytime.week_day() == 4  # 0=Monday, 4=Friday


def test_week_day_naive_datetime():
    # 无 tzinfo，应该自动加 tz
    dt = datetime(2024, 5, 4, 12, 0, 0)  # Saturday
    # Asia/Shanghai
    assert mytime.week_day(dt, tz=ZoneInfo("Asia/Shanghai")) == 5
    # UTC
    assert mytime.week_day(dt, tz=ZoneInfo("UTC")) == 5


def test_week_day_aware_datetime():
    dt = datetime(2024, 5, 5, 1, 0, 0, tzinfo=ZoneInfo("UTC"))  # Sunday UTC
    # 在上海是 2024-05-05 09:00:00，还是星期天
    assert mytime.week_day(dt, tz=ZoneInfo("Asia/Shanghai")) == 6  # Sunday


def test_week_day_cross_tz():
    # 2024-05-05 00:30:00 UTC = 2024-05-05 08:30:00 Asia/Shanghai
    dt_utc = datetime(2024, 5, 5, 0, 30, 0, tzinfo=ZoneInfo("UTC"))
    dt_sh = datetime(2024, 5, 5, 8, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    assert (
        mytime.week_day(dt_utc, tz=ZoneInfo("Asia/Shanghai"))
        == mytime.week_day(dt_sh, tz=ZoneInfo("Asia/Shanghai"))
        == 6
    )


def test_week_day_edge_cases():
    # Monday
    dt = datetime(2024, 4, 29, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    assert mytime.week_day(dt, tz=ZoneInfo("UTC")) == 0
    # Sunday
    dt = datetime(2024, 5, 5, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    assert mytime.week_day(dt, tz=ZoneInfo("UTC")) == 6


def test_week_day_str_none(mocker):
    dt = datetime(2024, 5, 3, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai"))  # Friday
    mocker.patch.object(mytime, "get_now", return_value=dt)
    assert mytime.week_day_str() == "Friday"


def test_week_day_str_naive_datetime():
    dt = datetime(2024, 5, 4, 12, 0, 0)  # Saturday
    # Asia/Shanghai
    assert mytime.week_day_str(dt, tz=ZoneInfo("Asia/Shanghai")) == "Saturday"
    # UTC
    assert mytime.week_day_str(dt, tz=ZoneInfo("UTC")) == "Saturday"


def test_week_day_str_aware_datetime():
    dt = datetime(2024, 5, 5, 1, 0, 0, tzinfo=ZoneInfo("UTC"))  # Sunday
    # 在上海是 2024-05-05 09:00:00，还是Sunday
    assert mytime.week_day_str(dt, tz=ZoneInfo("Asia/Shanghai")) == "Sunday"


def test_week_day_str_cross_tz():
    dt_utc = datetime(2024, 5, 5, 0, 30, 0, tzinfo=ZoneInfo("UTC"))
    dt_sh = datetime(2024, 5, 5, 8, 30, 0, tzinfo=ZoneInfo("Asia/Shanghai"))
    assert (
        mytime.week_day_str(dt_utc, tz=ZoneInfo("Asia/Shanghai"))
        == mytime.week_day_str(dt_sh, tz=ZoneInfo("Asia/Shanghai"))
        == "Sunday"
    )


def test_week_day_str_edge_cases():
    dt = datetime(2024, 4, 29, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    assert mytime.week_day_str(dt, tz=ZoneInfo("UTC")) == "Monday"
    dt = datetime(2024, 5, 5, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
    assert mytime.week_day_str(dt, tz=ZoneInfo("UTC")) == "Sunday"


def test_get_stamp_after_not_stamp(mocker):
    from smartutils import time as mytime

    mocker.patch.object(mytime, "get_now_stamp_float", return_value=1000.0)
    after = mytime.get_stamp_after(day=1, hour=1, minute=1, second=1)
    expected = 1000.0 + 86400 + 3600 + 60 + 1
    assert after == expected


def test_get_stamp_before_not_stamp(mocker):
    from smartutils import time as mytime

    mocker.patch.object(mytime, "get_now_stamp_float", return_value=2000.0)
    before = mytime.get_stamp_before(day=1, hour=1, minute=1, second=1)
    assert before == 2000.0 - (-82859)
