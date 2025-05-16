poetry install --all-extras
的意思是“安装所有在 [tool.poetry.extras] 中列出的分组所包含的依赖”。

自动创建激活虚拟环境
poetry install 安装主和dev

poetry install --with mysql,redis 安装主、dev、mysql、redis

dev-dependencies 只影响 smartutils 自己开发，不会被任何下游项目安装


poetry add 'git+ssh://git@192.168.1.56/nbcgai/smartutils.git@master#egg=smartutils&subdirectory=&extras=mysql,redis'

[tool.poetry.dependencies]
smartutils = { git = "ssh://git@192.168.1.56/nbcgai/smartutils.git", branch = "master", extras = ["mysql", "redis"] }


poetry add --dev pytest

poetry remove --dev pytest

poetry remove requests


生成 wheel 和 sdist：
poetry build
poetry config pypi-token.pypi mytoken
poetry publish --build

poetry shell

poetry run python script.py
poetry run pytest

poetry env info

移除虚拟环境：
poetry env remove python



pip也支持安装poetry标准的pyproject.toml


~1.4.5 
匹配“最小版本是 1.4.5，允许升级到下一个次版本（minor）但不允许到下一个主版本（major）”。
也就是说：允许自动升级 patch 号，但 minor 不能变。

^1.4.5
主版本号（major）不变，允许自动升级 minor 和 patch。

loguru = "^0.7.3" -> 允许 >=0.7.3, <0.8.0
redis = "~5.2.1" -> 允许 >=5.2.1, <5.3.0

主版本为 0 时（即 0.x.y），无论 ^ 还是 ~ 默认都只允许 patch 或 minor 升级，因为 0.x 代表不稳定开发。


workers 默认是多少？
workers 默认值是 1。
即：不设置 workers 时，Uvicorn 只启动一个进程来处理请求。
workers > 1 时的行为
当你设置 workers 大于 1，比如 workers=4：

Uvicorn 会启动一个主进程（master process），再启动指定数量的子进程（worker processes）。
每个 worker 是一个独立的 Python 进程，监听同一个端口（通常通过 SO_REUSEPORT 实现端口复用）。
worker 之间彼此独立，不共享内存或全局变量（这点和 Gunicorn 一样）。
增加 worker 数可以提升多核 CPU 下的并发能力和容错能力（一个 worker 崩溃不影响其他 worker）。
reload 选项与 workers 冲突：当 reload=True 时，workers 强制为 1（Uvicorn 会自动忽略你设置的多 worker）。
