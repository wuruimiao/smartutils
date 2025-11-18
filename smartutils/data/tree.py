from typing import Dict, List, Mapping, Sequence, Tuple

from smartutils.log import logger


def detect_cycle(id_to_parent: Dict) -> Tuple[bool, Dict]:
    """
    检测数据中是否存在循环引用（环），并返回去除环的映射。

    Args:
        id_to_parent (Dict): 节点ID到父节点ID的映射字典。

    Returns:
        Tuple[bool, Dict]: 第一个元素表示是否存在环，第二个元素是去除环后的节点ID到父节点ID的映射字典。
    """

    clean_map = id_to_parent.copy()
    has_cycle = False

    # 对每个节点进行深度优先搜索，检测是否存在环
    for node_id in list(id_to_parent.keys()):
        if node_id not in clean_map:
            continue  # 该节点可能已经在之前的循环中被移除

        visited = set()  # 当前路径上已访问的节点
        current = node_id
        path = [current]  # 记录路径，用于日志输出

        while current in clean_map and clean_map[current] != 0:
            current = clean_map[current]

            # 如果当前节点已经在访问路径中，说明存在环
            if current in visited:
                has_cycle = True
                cycle_path = path[path.index(current) :] + [current]
                logger.error(
                    f"检测到数据中存在循环引用: {' -> '.join(map(str, cycle_path))}"
                )

                # 找到环中最后出现的边，将其从映射中移除
                cycle_nodes = cycle_path[:-1]  # 不包括重复的最后一个节点
                last_node = cycle_nodes[-1]
                logger.error(f"移除成环边: {last_node} -> {clean_map[last_node]}")
                clean_map[last_node] = 0  # 将最后一个节点的父节点设为0（根节点）
                break

            visited.add(current)
            path.append(current)

    return has_cycle, clean_map


def make_parent(
    data: Sequence[Mapping],
    info_cls,
    data_key: str = "id",
    parent_key: str = "parent_id",
) -> Dict:
    """
    构建树形结构，将数据列表按父子关系组织成多叉树。
    如果检测到环，会去掉后出现的成环数据。

    Args:
        data (List[Mapping]): 输入的数据列表，每个元素为一个映射（如 dict），应包含主键和父键。
        info_cls: 用于实例化每个节点的数据类或对象，支持以 **row 方式初始化。
        data_key (str): 主键字段名，默认为 "id"。
        parent_key (str): 父节点字段名，默认为 "parent_id"。

    Returns:
        Dict: 顶层节点的字典（以主键为 key），每个节点应包含 children 属性（列表），子节点挂载在其下。
    """
    # 构建节点ID到父节点ID的映射
    id_to_parent = {row[data_key]: row.get(parent_key, 0) for row in data}

    # 检测是否存在环，并获取去除环后的映射
    _, clean_map = detect_cycle(id_to_parent)

    # 使用去除环后的映射构建树
    node_map = {row[data_key]: info_cls(**row) for row in data}
    result = {}

    for node_id, node in node_map.items():
        parent_id = clean_map.get(node_id, 0)  # 使用清理后的映射获取父节点ID
        if parent_id != 0:
            parent = node_map.get(parent_id)
            if parent:
                parent.children.append(node)
            else:
                # 没找到父亲，被视为孤儿
                result[node.id] = node
        else:
            # 纯顶层或被移除环的节点
            result[node.id] = node
    return result


def make_children(
    data: Sequence[Mapping],
    info_cls,
    data_key: str = "id",
    parent_key: str = "parent_id",
) -> Dict[int, List]:
    """
    构建每个节点的祖先路径（从根到当前节点）。
    如果检测到环，会去掉后出现的成环数据。

    Args:
        data (List[Mapping]): 输入的数据列表，每个元素为一个映射（如 dict），应包含主键和父键。
        info_cls: 用于实例化每个节点的数据类或对象，支持以 **row 方式初始化。
        data_key (str): 主键字段名，默认为 "id"。
        parent_key (str): 父节点字段名，默认为 "parent_id"。

    Returns:
        Dict[int, List]: 每个节点 id 映射到该节点的祖先路径（List），路径顺序为 [根, ..., 当前节点]。
    """
    # 构建节点ID到父节点ID的映射
    id_to_parent = {row[data_key]: row.get(parent_key, 0) for row in data}

    # 检测是否存在环，并获取去除环后的映射
    _, clean_map = detect_cycle(id_to_parent)

    node_map = {row[data_key]: info_cls(**row) for row in data}
    result = {}

    for node_id, node in node_map.items():
        path = []
        cur = node
        visited = set()  # 防止在构建路径时出现新的环

        while True:
            if cur.id in visited:  # 额外的安全检查
                logger.error(f"构建路径时检测到环: {cur.id} 已在路径中")
                break

            path.append(cur)
            visited.add(cur.id)

            parent_id = clean_map.get(cur.id, 0)  # 使用清理后的映射获取父节点ID
            if parent_id == 0 or parent_id not in node_map:
                break
            cur = node_map[parent_id]

        result[node_id] = list(reversed(path))
    return result
