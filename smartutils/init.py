async def init(conf_path: str = "config/config.yaml"):
    try:
        from smartutils.config import init, get_config, ConfKey

        init(conf_path)

        from smartutils.infra import init

        await init()

        from smartutils.ID import IDGen

        conf = get_config()
        IDGen.init(conf=conf.get(ConfKey.INSTANCE))
    except Exception as e:
        from smartutils.log import logger
        from smartutils.error.factory import ExcFormatFactory
        from smartutils.call import exit_on_fail
        logger.error(f"Smartutils init fail for: {ExcFormatFactory.get(e)}.")
        logger.error("App Exit.")
        exit_on_fail()


async def reset_all():
    """
    测试时重置单例状态类型，以及校验
    """
    from smartutils.design.singleton import reset_all

    reset_all()

    from smartutils.ctx import CTXVarManager

    CTXVarManager.reset_registered()

    from smartutils.infra.source_manager.manager import ResourceManagerRegistry

    await ResourceManagerRegistry.close_all()
