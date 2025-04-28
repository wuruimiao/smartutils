async def init():
    from smartutils.config import get_config
    config = get_config()

    import logging
    logger = logging.getLogger(__name__)

    global_vars = globals()

    from .factory import InfraFactory
    for comp_key, init_func in InfraFactory.all().items():
        conf = getattr(config, comp_key)
        if not conf:
            continue

        logger.info(f"initializing {comp_key} ...")
        instance = init_func(conf)
        global_vars[comp_key] = instance
        logger.info(f"{comp_key} inited.")
