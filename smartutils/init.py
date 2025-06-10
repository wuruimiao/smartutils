import traceback

__all__ = ["init"]


async def init(conf_path: str = "config/config.yaml"):
    try:
        from smartutils.config import ConfKey, get_config, init

        init(conf_path)

        from smartutils.infra import init

        await init()

        from smartutils.ID import IDGen

        conf = get_config()
        IDGen.init(conf=conf.get(ConfKey.INSTANCE))
    except Exception as e:
        from smartutils.call import exit_on_fail

        print(f"Smartutils init fail for: {e}")
        print(f"{traceback.format_exc()}")
        print("App Exit.")
        exit_on_fail()


async def reset_all():
    """
    测试时重置单例状态类型，以及校验
    以下会在import时初始化
        1. @CTXVarManager.register，reset后不会再触发，即使init也会报错：LibraryUsageError: CTXVarManager key
        2. @singleton，reset后，再次init时会创建，没问题
        3. @InfraFactory.register，reset后不会再触发，导致init时即使有配置也不会初始化，隐形错误
    """
    from smartutils.design.singleton import reset_all

    reset_all()

    # from smartutils.ctx import CTXVarManager

    # CTXVarManager.reset()

    from smartutils.infra.source_manager.manager import ResourceManagerRegistry

    await ResourceManagerRegistry.close_all()
