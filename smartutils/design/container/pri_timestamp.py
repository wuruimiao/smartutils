from smartutils.design.container.pri_dict_list import PriContainerDictList
from smartutils.time import get_now_stamp_float


class PriTSContainerDictList(PriContainerDictList):
    def put(self, value: object):
        return super().push(value, get_now_stamp_float())
