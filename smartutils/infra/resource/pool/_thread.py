from smartutils.design.condition._thread import ThreadCondition
from smartutils.design.condition_container.abstract import ConditionContainerProtocol
from smartutils.design.condition_container.base_sync import ConditionContainer
from smartutils.design.container.pri_timestamp import PriTSContainerDictList
from smartutils.infra.resource.pool.base_sync import ResourcePoolBase


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
