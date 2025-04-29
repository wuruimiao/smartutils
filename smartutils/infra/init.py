import inspect


async def init():
    from smartutils.config.init import _get_inner_config
    config = _get_inner_config()

    from smartutils.log import logger

    global_vars = globals()

    from smartutils.infra.factory import InfraFactory
    for comp_key, init_func in InfraFactory.all().items():
        conf = config.get(comp_key)
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
