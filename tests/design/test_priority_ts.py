from smartutils.design.container.pri_timestamp import PriTSContainerDictList


def test_pri_ts_dict_list():
    container = PriTSContainerDictList(reuse=True)
    container.put(1)
    container.put(2)
    container.put(3)
    assert container.pop_min() == 1
    assert container.pop_max() == 3
    assert container.remove(2) == 2
    assert len(container) == 0
