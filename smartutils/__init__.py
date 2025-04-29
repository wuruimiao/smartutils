__all__ = ['init_all']


async def init_all(log_f_name: str = None, conf_path: str = None):
    from smartutils.config import init
    init(conf_path)

    from smartutils.log import init
    init(log_f_name)

    from smartutils.infra import init
    await init()
