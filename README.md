

TODO: 如何管理开发和生产环境的依赖

pip install git+https://github.com/psf/black

sudo apt-get install graphviz

pydeps smartutils --exclude site-packages

lint-imports


## 单元测试
pytest -s --cov=smartutils --cov-report=html tests/ tests_real/


