import sys
from pathlib import Path

from smartutils.config.const import ConfKey
from smartutils.config.schema.logger import LoguruConfig
from smartutils.ctx import ContextVarManager, CTXKey
from smartutils.design import singleton
from smartutils.infra.abstract import AbstractResource
from smartutils.infra.factory import InfraFactory
from smartutils.infra.manager import ContextResourceManager
from smartutils.log import logger


class PrintToLogger:
    def write(self, message):
        message = message.strip()
        if message:
            logger.debug(message)

    def flush(self):
        pass


class LoggerCli(AbstractResource):
    def __init__(self, conf: LoguruConfig, name: str):
        self._name = name
        self._conf = conf
        self._format = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                        "<level>{level: <8}</level> | "
                        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                        "<magenta>{extra[trace_id]}</magenta> - <level>{message}</level>")
        self._init()

    def _init(self):
        logger.remove()
        logger.configure(patcher=self.inject_trace_id)

        from smartutils.config import get_config

        _conf = get_config()

        if not self._conf:
            logger.info(f'init logger: config no loguru key, do nothing')
            return

        if self._conf.stream:
            kw = self._conf.stream_kw
            kw['format'] = self._format
            kw['colorize'] = True
            logger.add(sys.stdout, **kw)

        if self._conf.logdir:
            project_name = 'app' if not _conf.project else _conf.project.name
            file_path = Path(self._conf.logdir) / f'{project_name}.log'
            file_path.parent.mkdir(parents=True, exist_ok=True)

            kw = self._conf.file_kw
            kw['format'] = self._format
            kw['colorize'] = False
            logger.add(file_path, **kw)

        if not self._conf.stream and self._conf.logdir:
            sys.stdout = PrintToLogger()
            sys.stderr = PrintToLogger()

    @ContextVarManager.register(CTXKey.TRACE_ID)
    def inject_trace_id(self, record):
        record["extra"]["trace_id"] = ContextVarManager.get(CTXKey.TRACE_ID, default='-')
        return True

    async def close(self):
        logger.remove()

    async def ping(self) -> bool:
        return True

    async def session(self):
        pass


@singleton
class LoggerManager(ContextResourceManager[LoggerCli]):
    def __init__(self, conf):
        resources = {'logger': LoggerCli(conf, 'logger')}
        super().__init__(resources, 'logger')


@InfraFactory.register(ConfKey.LOGURU)
def init_loguru_log(conf: LoguruConfig):
    return LoggerManager(conf)
