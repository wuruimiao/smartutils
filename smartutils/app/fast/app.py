def create_app():
    from contextlib import asynccontextmanager

    from fastapi import FastAPI
    from smartutils.app.fast.middlewares import HeaderMiddleware
    from smartutils.ret import ResponseModel

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        from smartutils.config import init, get_config
        init()

        from smartutils.infra import init
        await init()

        from smartutils.ID import SnowflakeGenerator
        _app.state.gen = SnowflakeGenerator(instance=get_config().project.id)

        yield

        from smartutils.log import logger
        logger.info(f'shutdown start close')
        from smartutils import release
        await release()
        logger.info(f'shutdown all closed')

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(HeaderMiddleware)

    @app.get('/')
    def root() -> ResponseModel:
        return ResponseModel()

    @app.get('/healthy')
    def healthy() -> ResponseModel:
        return ResponseModel()

    return app
