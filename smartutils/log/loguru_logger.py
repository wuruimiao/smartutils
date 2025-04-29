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

    conf = get_config()
    project_name = 'app' if not conf.project else conf.project.name
    conf = conf.get(ConfKey.LOGURU)

    if not conf:
        logger.info(f'init logger: config no loguru key, do nothing')
        return

    if conf.stream:
        logger.add(
            sys.stdout,
            level=conf.level,
            format=_FORMAT,
            colorize=True,
            enqueue=conf.enqueue,
        )

    if conf.logdir:
        file_path = Path(conf.logdir) / f'{project_name}.log'
        file_path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(
            file_path,
            level=conf.level,
            format=_FORMAT,
            rotation=conf.rotation,
            retention=conf.retention,
            compression=conf.compression,
            enqueue=conf.enqueue,
            colorize=False,
        )

    if not conf.stream and conf.logdir:
        sys.stdout = PrintToLogger()
        sys.stderr = PrintToLogger()
