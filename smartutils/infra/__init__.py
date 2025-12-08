"""
基础设施模块
管理：各种资源管理器，如MySQL、Redis等，底层client必须实现AbstractAsyncResource接口，
     以统一管理资源的声明使用、心跳检测、异常处理、关闭等生命周期操作。
"""

from smartutils.infra.alert.feishu import AlertFeishuManager
from smartutils.infra.cache.redis import RedisManager
from smartutils.infra.client.manager import ClientManager
from smartutils.infra.db.mongo import MongoManager
from smartutils.infra.db.mysql import MySQLManager
from smartutils.infra.db.postgresql import PostgresqlManager
from smartutils.infra.log.loguru import LoggerManager
from smartutils.infra.mq.cli import KafkaBatchConsumer
from smartutils.infra.mq.kafka import KafkaManager
from smartutils.infra.resource.manager.manager import (
    CTXResourceManager,
    ResourceManagerRegistry,
)
from smartutils.infra.tencentcloud.manager import TencentCloudManager

__all__ = [
    "ResourceManagerRegistry",
    "CTXResourceManager",
    "RedisManager",
    "MySQLManager",
    "PostgresqlManager",
    "MongoManager",
    "KafkaManager",
    "KafkaBatchConsumer",
    "ClientManager",
    "LoggerManager",
    "AlertFeishuManager",
    "TencentCloudManager",
]
