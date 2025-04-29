import sys
from pathlib import Path

from loguru import logger

from smartutils.ctx import ContextVarManager, CTXKey

_FORMAT = ("<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<magenta>{extra[trace_id]}</magenta> - <level>{message}</level>")


@ContextVarManager.register(CTXKey.TRACE_ID)
def inject_trace_id(record):
    record["extra"]["trace_id"] = ContextVarManager.get(CTXKey.TRACE_ID, default='-')
    return True


class PrintToLogger:
    def write(self, message):
        message = message.strip()
        if message:
            logger.debug(message)

    def flush(self):
        pass


def init():
    logger.remove()

    logger.configure(patcher=inject_trace_id)

    from smartutils.config import get_config, ConfKey
    from smartutils.config.schema.logger import LoguruConfig

    _conf = get_config()
    conf: LoguruConfig = _conf.get(ConfKey.LOGURU)

    if not conf:
        logger.info(f'init logger: config no loguru key, do nothing')
        return

    if conf.stream:
        kw = conf.stream_kw
        kw['format'] = _FORMAT
        kw['colorize'] = True
        logger.add(sys.stdout, **kw)

    if conf.logdir:
        project_name = 'app' if not _conf.project else _conf.project.name
        file_path = Path(conf.logdir) / f'{project_name}.log'
        file_path.parent.mkdir(parents=True, exist_ok=True)

        kw = conf.file_kw
        kw['format'] = _FORMAT
        kw['colorize'] = False
        logger.add(file_path, **kw)

    if not conf.stream and conf.logdir:
        sys.stdout = PrintToLogger()
        sys.stderr = PrintToLogger()
