"""
smartutils.app.adapter.json_resp
--------------------------------

本包为各主流 Web 框架（如 FastAPI、Flask、Django、Tornado、Sanic、Aiohttp）提供统一的 JSON 响应输出适配器。

设计目标：
    - 实现不同 Web 框架下标准化的 JSON 响应格式
    - 结合 smartutils.error 体系，实现错误及数据响应的解耦与扩展

包内文件说明：
    - _fastapi.py   : FastAPI 专用的 JSON 响应工厂与适配工具
    - flask.py      : Flask 响应适配
    - django.py     : Django 响应适配
    - tornado.py    : Tornado 响应适配
    - sanic.py      : Sanic 响应适配
    - aiohttp.py    : Aiohttp 响应适配
    - factory.py    : 通用 JSON 响应工厂/适配基础类

典型用途：
    在smartutils/app/__init__.py中，通过register_package(_adapter)，解析并import smartutils.app.adapter下的包，触发注册，从而启用统一风格和扩展能力的 API 响应。

"""
