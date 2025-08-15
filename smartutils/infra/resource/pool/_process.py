from smartutils.design.condition._process import ProcessCondition
from smartutils.design.condition_container.base import ConditionContainer
from smartutils.design.container.pri_timestamp import PriTSContainerDictList
from smartutils.infra.resource.pool.base import ResourcePoolBase


class ProcessPriPool(ResourcePoolBase):
    def __init__(self, manager) -> None:
        super().__init__(
            container=ConditionContainer(
                container=PriTSContainerDictList(),
                condition=ProcessCondition(manager=manager),
            )
        )
