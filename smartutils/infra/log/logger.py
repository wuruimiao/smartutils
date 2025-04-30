import sys
from pathlib import Path

from smartutils.config.const import ConfKeys
from smartutils.config.schema.logger import LoguruConfig
from smartutils.ctx import CTXVarManager, CTXKeys
from smartutils.design import singleton
from smartutils.infra.abstract import AbstractResource
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import CTXResourceManager
from smartutils.log import logger


class PrintToLogger:
    def write(self, message):  # noqa
        message = message.strip()
        if message:
            logger.debug(message)

    def flush(self):
        pass


class LoggerCli(AbstractResource):
    def __init__(self, conf: LoguruConfig, name: str):
        self._name = name
        self._conf = conf
        self._format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<magenta>{extra[trace_id]}</magenta> - <level>{message}</level>"
        )
        self._init()

    def _init(self):
        logger.remove()
        logger.configure(patcher=self._inject_trace_id)

        from smartutils.config import get_config

        _conf = get_config()

        if not self._conf:
            logger.debug(f"LoggerCli init, config no loguru key, ignore.")
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

    @CTXVarManager.register(CTXKeys.TRACE_ID)
    def _inject_trace_id(self, record):
        record["extra"]["trace_id"] = CTXVarManager.get(CTXKeys.TRACE_ID, default="0")
        return True

    async def close(self):
        logger.remove()

    async def ping(self) -> bool:
        return True

    async def session(self):
        pass


@singleton
class LoggerManager(CTXResourceManager[LoggerCli]):
    def __init__(self, conf):
        resources = {ConfKeys.GROUP_DEFAULT: LoggerCli(conf, "logger_loguru")}
        super().__init__(resources, CTXKeys.NO_USE)


@InfraFactory.register(ConfKeys.LOGURU)
def init_loguru(conf: LoguruConfig):
    return LoggerManager(conf)
