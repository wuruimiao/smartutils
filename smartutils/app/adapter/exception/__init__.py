"""
smartutils.app.adapter.exception
--------------------------------

本包为各主流 Web 框架（如 FastAPI、Flask、Django、Tornado、Sanic、Aiohttp）提供统一的异常适配器。

设计目标：
    - 归一化不同 Web 框架的异常处理与自定义异常抛出/转换流程
    - 依赖 smartutils.error.factory 提供的异常分派、提取、标准化能力，实现框架无关的统一异常返回逻辑
    - 如依赖ExcErrorFactory，将框架特有异常（如 FastAPI 的 RequestValidationError）转换为统一的业务异常（如 ValidationError）
    - 如依赖ExcDetailFactory，提取异常的详细描述信息，支持日志记录和调试
    - 支持不同框架生态下的自定义错误实现（如 RequestValidationError 适配、HTTPException 归一、内置与第三方异常的标准转化）
    - 提供开发者按需扩展、继承、注入适配逻辑的基础模块

包内文件说明：
    - fastapi.py   : FastAPI 相关的异常适配与自定义错误处理流
    - flask.py     : Flask 相关适配
    - django.py    : Django 相关适配
    - tornado.py   : Tornado 相关适配
    - sanic.py     : Sanic 相关适配
    - aiohttp.py   : Aiohttp 相关适配

典型用途：
    在smartutils/app/__init__.py中，通过register_package(_adapter)，解析并import smartutils.app.adapter下的包，触发注册，从而启用统一的异常适配功能。

"""
