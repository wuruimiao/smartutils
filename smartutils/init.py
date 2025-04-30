async def init(conf_path: str = "config/config.yaml"):
    from smartutils.config import init

    init(conf_path)

    from smartutils.infra import init

    await init()


async def reset_all():
    """
    测试时重置单例状态类型，以及校验
    """
    from smartutils.design.singleton import reset_all

    reset_all()

    from smartutils.ctx import CTXVarManager

    CTXVarManager.reset_registered()

    from smartutils.infra.manager import ResourceManagerRegistry

    await ResourceManagerRegistry.close_all()
