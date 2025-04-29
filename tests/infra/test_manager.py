import pytest
from smartutils.infra.manager import ContextResourceManager


def test_context_var_name_unique():
    mgr1 = ContextResourceManager({}, "my_var")
    with pytest.raises(ValueError):
        ContextResourceManager({}, "my_var")


# async def test_init(tmp_path_factory):
#     config_str = """
#     mysql:
#       default:
#         host: localhost
#         port: 3306
#         user: root
#         passwd: naobo
#         db: test_db
#         pool_size: 10
#         max_overflow: 5
#         pool_timeout: 30
#         pool_recycle: 3600
#         echo: false
#         echo_pool: false
#         connect_timeout: 10
#         execute_timeout: 10"""
#     tmp_dir = tmp_path_factory.mktemp("config")
#     config_file = tmp_dir / "test_config.yaml"
#     with open(config_file, "w") as f:
#         f.write(config_str)
#     from smartutils.config import init
#     init(str(config_file))
#
#     from smartutils.infra.factory import InfraFactory
#
#     @InfraFactory.register('mysql')
#     async def init(conf):
#         pass
#
#     from smartutils.infra import init
#     await init()
#
#     from smartutils import reset_all
#     reset_all()
