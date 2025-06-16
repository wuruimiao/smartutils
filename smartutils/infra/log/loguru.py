import sys
from contextlib import asynccontextmanager
from pathlib import Path

from smartutils.config.const import ConfKey
from smartutils.config.schema.loguru import LoguruConfig
from smartutils.ctx import CTXKey, CTXVarManager
from smartutils.design import singleton
from smartutils.infra.factory import InfraFactory
from smartutils.infra.source_manager.abstract import AbstractResource
from smartutils.infra.source_manager.manager import CTXResourceManager
from smartutils.log import logger

__all__ = ["LoggerManager"]


class PrintToLogger:
    def write(self, message):  # noqa
        message = message.strip()
        if message:
            logger.debug(message)

    def flush(self):
        pass


class LoggerCli(AbstractResource):
    """loguru.logger线程安全、协程安全"""

    def __init__(self, conf: LoguruConfig, name: str):
        self._name = name
        self._conf = conf
        self._format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<magenta>trace_id={extra[trace_id]}</magenta> "
            "<yellow>userid={extra[userid]}</yellow> "
            "<blue>username={extra[username]}</blue> - <level>{message}</level>"
        )
        self._init()

    @staticmethod
    def _inject(record):
        record["extra"]["trace_id"] = CTXVarManager.get(CTXKey.TRACE_ID, default="")
        record["extra"]["userid"] = CTXVarManager.get(CTXKey.USERID, default="")
        record["extra"]["username"] = CTXVarManager.get(CTXKey.USERNAME, default="")
        return record

    def _init(self):
        logger.remove()
        logger.configure(patcher=self._inject)

        from smartutils.config import get_config

        _conf = get_config()

        if not self._conf:
            logger.debug("LoggerCli init, config no loguru key, ignore.")
            return

        if self._conf.stream:
            kw = self._conf.stream_kw
            kw["format"] = self._format
            kw["colorize"] = True
            logger.add(sys.stdout, **kw)

        if self._conf.logdir:
            project_name = "app" if not _conf.project else _conf.project.name
            file_path = Path(self._conf.logdir) / f"{project_name}.log"
            file_path.parent.mkdir(parents=True, exist_ok=True)

            kw = self._conf.file_kw
            kw["format"] = self._format
            kw["colorize"] = False
            logger.add(file_path, **kw)

        if not self._conf.stream and self._conf.logdir:
            sys.stdout = PrintToLogger()
            sys.stderr = PrintToLogger()

    async def close(self):
        logger.remove()

    async def ping(self) -> bool:
        return True

    @asynccontextmanager
    async def db(self, use_transaction: bool = False):
        yield logger


@singleton
@CTXVarManager.register(CTXKey.LOGGER_LOGURU)
class LoggerManager(CTXResourceManager[LoggerCli]):
    def __init__(self, conf):
        resources = {ConfKey.GROUP_DEFAULT: LoggerCli(conf, "logger_loguru")}
        super().__init__(resources, CTXKey.LOGGER_LOGURU)


@InfraFactory.register(ConfKey.LOGURU)
def _(conf: LoguruConfig):
    return LoggerManager(conf)
