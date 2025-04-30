import inspect


async def init():
    from smartutils.config.init import get_config

    config = get_config()

    from smartutils.log import logger

    from smartutils.infra.factory import InfraFactory

    for comp_key, init_func in InfraFactory.all().items():
        conf = config.get(comp_key)
        if not conf:
            logger.debug(f"infra init config no {comp_key}, ignore.")
            continue

        logger.debug(f"infra initializing {comp_key} ...")
        if inspect.iscoroutinefunction(init_func):
            await init_func(conf)
        else:
            init_func(conf)

        logger.info(f"infra {comp_key} inited.")


async def release():
    from smartutils.infra.manager import ResourceManagerRegistry

    await ResourceManagerRegistry.close_all()
