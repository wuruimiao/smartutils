from smartutils.design.condition._async import AsyncioCondition
from smartutils.design.condition_container.base import AsyncConditionContainer
from smartutils.design.container.pri_timestamp import PriTSContainerDictList
from smartutils.infra.resource.pool.base_async import AsyncResourcePoolBase


class AsyncPriPool(AsyncResourcePoolBase):
    def __init__(self) -> None:
        super().__init__(
            container=AsyncConditionContainer(
                container=PriTSContainerDictList(), condition=AsyncioCondition()
            )
        )
