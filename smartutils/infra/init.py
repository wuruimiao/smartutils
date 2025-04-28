import inspect


async def init():
    from smartutils.config import get_config
    config = get_config()

    import logging
    logger = logging.getLogger(__name__)

    global_vars = globals()

    from smartutils.infra.factory import InfraFactory
    for comp_key, init_func in InfraFactory.all().items():
        conf = getattr(config, comp_key, None)
        if not conf:
            logger.info(f'config no {comp_key}, do nothing')
            continue

        logger.info(f"initializing {comp_key} ...")
        if inspect.iscoroutinefunction(init_func):
            instance = await init_func(conf)
        else:
            instance = init_func(conf)

        global_vars[comp_key] = instance
        logger.info(f"{comp_key} inited.")
