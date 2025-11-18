from collections import OrderedDict


def remove_duplicate(data: list, save_first=False):
    if not save_first:
        return list(OrderedDict.fromkeys(data))
    exist = set()
    result = [exist.add(item) or item for item in data if item not in exist]
    return result
