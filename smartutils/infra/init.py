from smartutils.call import call_hook

__all__ = ["init", "release"]


async def init():
    from smartutils.config.init import get_config

    config = get_config()

    from smartutils.log import logger

    from smartutils.infra.factory import InfraFactory

    for comp_key, info in InfraFactory.all():
        init_func, need_conf = info
        conf = config.get(comp_key)
        if need_conf and not conf:
            logger.debug("infra init config no {comp_key}, ignore.", comp_key=comp_key)
            continue

        logger.debug("infra initializing {comp_key} ...", comp_key=comp_key)

        await call_hook(init_func, conf)

        logger.info("infra {comp_key} inited.", comp_key=comp_key)


async def release():
    from smartutils.infra.source_manager.manager import ResourceManagerRegistry

    await ResourceManagerRegistry.close_all()
