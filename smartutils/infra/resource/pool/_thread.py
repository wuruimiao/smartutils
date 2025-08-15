from smartutils.design.condition._thread import ThreadCondition
from smartutils.design.condition_container.base import ConditionContainer
from smartutils.design.pri_container.imp import PriTSContainerDictList
from smartutils.infra.resource.pool.base import ResourcePoolBase


class ThreadPriTSPool(ResourcePoolBase):
    def __init__(self) -> None:
        super().__init__(
            container=ConditionContainer(
                container=PriTSContainerDictList(), condition=ThreadCondition()
            )
        )


class ThreadQueuePool(ResourcePoolBase):
    def __init__(self) -> None:
        super().__init__(container=None)
