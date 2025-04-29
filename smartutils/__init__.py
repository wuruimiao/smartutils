__all__ = ['init_all']


async def init_all(conf_path: str = 'config/config.yaml'):
    from smartutils.config import init
    init(conf_path)

    from smartutils.log import init
    init()

    from smartutils.infra import init
    await init()


def reset_all():
    """
    测试时重置单例状态类型，以及校验
    """
    from smartutils.design.singleton import reset_all
    reset_all()

    from smartutils.ctx import ContextVarManager
    ContextVarManager.reset_registered()
