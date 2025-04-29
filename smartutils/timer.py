import contextlib
from time import perf_counter

from smartutils.log import logger
from smartutils.time import get_now_stamp


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
