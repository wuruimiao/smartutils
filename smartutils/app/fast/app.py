from contextlib import asynccontextmanager
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    from smartutils.init import init

    await init()

    from smartutils.config import get_config
    from smartutils.ID import SnowflakeGenerator

    conf = get_config()
    app.state.gen = SnowflakeGenerator(instance=conf.project.id)

    app.title = conf.project.name
    app.version = conf.project.version
    app.description = conf.project.description

    yield

    from smartutils.log import logger

    logger.info(f"shutdown start close")
    from smartutils import release

    await release()
    logger.info(f"shutdown all closed")


def create_app():
    from smartutils.app.fast.middlewares import HeaderMiddleware
    from smartutils.ret import ResponseModel

    app = FastAPI(lifespan=lifespan)

    app.add_middleware(HeaderMiddleware)

    @app.get("/")
    def root() -> ResponseModel:
        return ResponseModel()

    @app.get("/healthy")
    def healthy() -> ResponseModel:
        return ResponseModel()

    return app
