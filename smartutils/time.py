import contextlib
import logging
from datetime import datetime
from datetime import timedelta
from time import time, perf_counter
from typing import Tuple

logger = logging.getLogger(__name__)

_DefaultFormat = "%Y-%m-%d %H:%M:%S"


def format_time(t: datetime, f: str = _DefaultFormat) -> str:
    """
    格式化时间
    :param t:
    :param f:
    :return:
    """
    return t.strftime(f)


def format_timestamp(timestamp: int) -> str:
    dt = datetime.utcfromtimestamp(timestamp) + timedelta(hours=8)
    return format_time(dt)


def get_now():
    """
    获取当前时间
    :return:
    """
    return datetime.now()


def get_now_str() -> str:
    return format_time(get_now())


def today() -> str:
    return format_time(get_now(), "%Y-%m-%d")


def yesterday() -> str:
    return format_time(get_now() - timedelta(days=1), "%Y-%m-%d")


def get_now_stamp() -> int:
    """
    获取当前时间戳
    :return:
    """
    return int(get_now_stamp_float())


def get_now_stamp_float() -> float:
    return time()


def get_now_stamp_str() -> str:
    return str(get_now_stamp_float())


def get_stamp_after(stamp: float = None,
                    day: int = 0, hour: int = 0, minute: int = 0, second: int = 0) -> float:
    """
    获取一段时间后的时间戳
    :param stamp:
    :param day:
    :param hour:
    :param minute:
    :param second:
    :return:
    """
    if not stamp:
        stamp = get_now_stamp_float()
    if day:
        hour += day * 24
    if hour:
        minute += hour * 60
    if minute:
        second += minute * 60
    return stamp + second


def get_stamp_before(stamp: float=None,
                     day: int = 0, hour: int = 0, minute: int = 0, second: int = 0) -> float:
    if not stamp:
        stamp = get_now_stamp_float()
    if day:
        hour -= day * 24
    if hour:
        minute -= hour * 60
    if minute:
        second -= minute * 60
    return stamp - second

def get_pass_time(early: datetime, latest: datetime) -> Tuple[int, int, int, int]:
    """
    获取已经过去了多少天、时、分
    Args:
        early:
        latest:

    Returns:

    """
    d = latest - early
    return d.days, d.seconds // 3600, (d.seconds // 60) % 60, d.seconds % 3600 % 60


def get_remain_time(early: datetime, latest: datetime, day: int, hour: int, minute: int, second: int) -> \
        Tuple[int, int, int, int]:
    """

    Args:
        early: 记录生成的时间点
        latest: 最新的时间点
        day: 记录的天数
        hour: 记录的小时数
        minute: 记录的分钟数
        second: 记录的秒数

    Returns: 距离记录的截止时间，还有多少天、时、分
    """
    deadline = early + timedelta(days=day, hours=hour, minutes=minute, seconds=second)
    if deadline <= latest:
        return 0, 0, 0, 0
    return get_pass_time(latest, deadline)


def parse_time_str(time_str: str, str_format: str = _DefaultFormat) -> datetime:
    """
    :param time_str:
    :param str_format:
    :return:
    """
    return datetime.strptime(time_str, str_format)


def get_timestamp(t: datetime) -> float:
    return t.timestamp()


class Timer:
    def __init__(self, func=perf_counter):
        self.elapsed = 0.0
        self._func = func
        self._start = None

    def start(self):
        if self._start is not None:
            raise RuntimeError('Already started')
        self._start = self._func()

    def stop(self):
        if self._start is None:
            raise RuntimeError('Not started')
        end = self._func()
        self.elapsed += end - self._start
        self._start = None

    def reset(self):
        self.elapsed = 0.0

    @property
    def running(self):
        return self._start is not None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
        logger.info(f"cost {self.elapsed}")


@contextlib.contextmanager
def timer(log):
    start = get_now_stamp()
    yield
    logger.info(f"{log} cost {(get_now_stamp() - start) / 60} min")


class TimeRecord:
    def __init__(self):
        self._last = get_now_stamp()

    def record(self, t=None):
        if t is None:
            t = get_now_stamp()
        self._last = t

    def gap_up_to(self, sec: int) -> bool:
        return get_now_stamp() - self._last > sec


def week_day(date=get_now()):
    return date.weekday()


def week_day_str(date=get_now()):
    return date.strftime('%A')


def today_remain_sec() -> int:
    now = datetime.now()
    end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
    delta = end_of_day - now
    return int(delta.total_seconds())
