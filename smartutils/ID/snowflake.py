from dataclasses import dataclass
from time import time
from typing import Optional
from datetime import datetime, timedelta, tzinfo, timezone


# ========== 雪花ID算法常量 ==========
MAX_TS = 0b11111111111111111111111111111111111111111  # 41位，最大时间戳差（毫秒）
MAX_INSTANCE = 0b1111111111  # 10位，最大机器/进程号
MAX_SEQ = 0b111111111111  # 12位，最大序列号


@dataclass(frozen=True)
class Snowflake:
    """
    雪花ID实体对象，支持反解各组成部分。
    """

    timestamp: int
    instance: int
    epoch: int = 0
    seq: int = 0

    def __post_init__(self):
        if self.epoch < 0:
            raise ValueError("epoch must not be negative!")
        if not (0 <= self.timestamp <= MAX_TS):
            raise ValueError(f"timestamp must be in [0, {MAX_TS}]!")
        if not (0 <= self.instance <= MAX_INSTANCE):
            raise ValueError(f"instance must be in [0, {MAX_INSTANCE}]!")
        if not (0 <= self.seq <= MAX_SEQ):
            raise ValueError(f"seq must be in [0, {MAX_SEQ}]!")

    @classmethod
    def parse(cls, snowflake: int, epoch: int = 0) -> "Snowflake":
        """
        解析整数雪花ID为 Snowflake 对象
        """
        return cls(
            epoch=epoch,
            timestamp=snowflake >> 22,
            instance=(snowflake >> 12) & MAX_INSTANCE,
            seq=snowflake & MAX_SEQ,
        )

    @property
    def milliseconds(self) -> int:
        """
        返回雪花ID对应的绝对毫秒时间戳（自 epoch 起）
        """
        return self.timestamp + self.epoch

    @property
    def seconds(self) -> float:
        """
        返回雪花ID对应的时间戳（单位秒）
        """
        return self.milliseconds / 1000

    @property
    def datetime(self) -> datetime:
        """
        返回 UTC 时区的 datetime
        """
        return datetime.fromtimestamp(self.seconds, tz=timezone.utc)

    def datetime_tz(self, tz: Optional[tzinfo] = None) -> datetime:
        """
        返回指定时区的 datetime
        """
        return datetime.fromtimestamp(self.seconds, tz=tz)

    @property
    def timedelta(self) -> timedelta:
        """
        返回自定义 epoch 的 timedelta
        """
        return timedelta(milliseconds=self.epoch)

    @property
    def value(self) -> int:
        """
        返回当前 Snowflake 对象的整数值
        """
        return (self.timestamp << 22) | (self.instance << 12) | self.seq

    def __int__(self) -> int:
        return self.value

    def __repr__(self):
        return (
            f"Snowflake(timestamp={self.timestamp}, instance={self.instance}, "
            f"seq={self.seq}, epoch={self.epoch}, value={self.value})"
        )


class SnowflakeGenerator:
    """
    雪花ID生成器，支持迭代调用和直接调用。
    每个实例代表一个节点/进程的ID生成器。
    """

    def __init__(
        self,
        instance: int,
        *,
        seq: int = 0,
        epoch: int = 0,
        timestamp: Optional[int] = None,
    ):
        """
        :param instance: 当前节点/进程编号（0~1023）
        :param seq: 序列号初始值（一般用默认）
        :param epoch: 自定义起始时间戳（毫秒），建议为系统部署时间
        :param timestamp: 可选，指定初始时间戳（毫秒）
        """
        current = int(time() * 1000)
        if current - epoch >= MAX_TS:
            raise OverflowError(
                "The maximum current timestamp has been reached in selected epoch, "
                "so Snowflake cannot generate more IDs!"
            )
        timestamp = timestamp or current
        if timestamp < 0 or timestamp > current:
            raise ValueError(f"timestamp must be in [0, {current}]!")
        if epoch < 0 or epoch > current:
            raise ValueError(f"epoch must be in [0, {current}]!")
        if instance < 0 or instance > MAX_INSTANCE:
            raise ValueError(f"instance must be in [0, {MAX_INSTANCE}]!")
        if seq < 0 or seq > MAX_SEQ:
            raise ValueError(f"seq must be in [0, {MAX_SEQ}]!")

        self._epo = epoch
        self._ts = timestamp - epoch
        self._inf = instance << 12
        self._seq = seq

    @classmethod
    def from_snowflake(cls, sf: Snowflake) -> "SnowflakeGenerator":
        """
        通过 Snowflake 对象恢复生成器
        """
        return cls(sf.instance, seq=sf.seq, epoch=sf.epoch, timestamp=sf.timestamp)

    @property
    def epoch(self) -> int:
        """
        获取当前生成器的 epoch
        """
        return self._epo

    def __iter__(self):
        return self

    def __next__(self) -> int:
        """
        生成下一个唯一ID（int）。如本毫秒内序列号溢出，则等待下一毫秒。
        """
        current = int(time() * 1000) - self._epo

        if current >= MAX_TS:
            raise StopIteration(
                "The maximum current timestamp has been reached in selected epoch, "
                "so Snowflake cannot generate more IDs!"
            )

        if self._ts == current:
            if self._seq == MAX_SEQ:
                # 若序列号溢出，自动等待下一毫秒
                while int(time() * 1000) - self._epo <= current:
                    pass  # busy wait
                self._seq = 0
                self._ts = int(time() * 1000) - self._epo
            else:
                self._seq += 1
        elif self._ts > current:
            raise StopIteration("Clock moved backwards?")
        else:
            self._seq = 0
            self._ts = current

        return (self._ts << 22) | self._inf | self._seq

    def __call__(self) -> int:
        """
        直接调用生成下一个唯一ID（int）
        """
        return next(self)

    def next_snowflake(self) -> Snowflake:
        """
        生成下一个 Snowflake 实例对象
        """
        val = next(self)
        return Snowflake.parse(val, epoch=self._epo)

    def __repr__(self):
        return f"<SnowflakeGenerator(epoch={self._epo})>"
