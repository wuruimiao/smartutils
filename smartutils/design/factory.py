import sys
from abc import ABC
from collections import OrderedDict, defaultdict, deque
from dataclasses import dataclass
from typing import (
    Callable,
    Generic,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    final,
)

from smartutils.design._class import MyBase
from smartutils.error.sys import LibraryError, LibraryUsageError

# key类型，同一key根据配置会覆盖/报错
K = TypeVar("K")
# value类型，register装饰的类/函数
V = TypeVar("V")
# 附加元信息，可选。
MetaT = TypeVar("MetaT", bound=object)


@dataclass
class Entry(Generic[V, MetaT]):
    v: V
    meta: Optional[MetaT] = None


class BaseFactory(Generic[K, V, MetaT], ABC, MyBase):
    # 从小达到维护顺序
    _registry_value: OrderedDict[K, Entry[V, MetaT]]
    _registry_order: dict[K, int]
    _registry_deps: dict[K, set[K]]
    _sorted_keys: Optional[Tuple[K, ...]]

    def __init_subclass__(cls):
        cls._registry_value = OrderedDict()
        cls._registry_order = {}
        cls._registry_deps = defaultdict(set)
        cls._sorted_keys = None
        # cls.name = f"[{cls.__name__}]"

    @classmethod
    @final
    def _reset_cache(cls):
        cls._sorted_keys = None

    @classmethod
    @final
    def reset(cls):
        cls._registry_value.clear()
        cls._registry_order.clear()
        cls._registry_deps.clear()
        cls._reset_cache()

    @classmethod
    @final
    def _with_deps_all(cls):  # pragma: no cover
        # 拓扑排序
        in_degrees = {k: 0 for k in cls._registry_value.keys()}
        graph = {k: [] for k in cls._registry_value.keys()}
        # 构建图
        for k, deps in cls._registry_deps.items():
            for d in deps:
                if d not in cls._registry_value:
                    raise LibraryError(  # pragma: no cover
                        f"{cls.name} require register {d} before register {k}."
                    )
                graph[d].append(k)  # 依赖项指向节点，后续需先处理完依赖项，再处理节点
                in_degrees[k] += 1  # 入度和依赖项挂钩，即k的依赖数量

        # Kahn算法
        # 先处理没有依赖的
        queue = deque([k for k, deg in in_degrees.items() if deg == 0])
        topo = []
        while queue:
            node = queue.popleft()  # 包括原来都没有的，以及已处理完所有依赖项的k
            topo.append(node)
            for neighbor in graph[node]:  # 找到依赖node的节点
                in_degrees[neighbor] -= 1  # 依赖node的节点依赖数减1
                if in_degrees[neighbor] == 0:  # 依赖node的节点没有依赖项未处理了
                    queue.append(neighbor)

        if len(topo) != len(cls._registry_value):  # 有节点的依赖项一直没处理
            raise LibraryError(f"{cls.name} deps cycle detected.")  # pragma: no cover

        # 重新整理有序字典
        new_order = OrderedDict()
        for k in topo:
            new_order[k] = cls._registry_value[k]
        cls._registry_value = new_order

    @classmethod
    @final
    def _with_deps(cls, key: K, deps: Sequence[K]) -> int:  # pragma: no cover
        """
        根据依赖，找到_registry_value的插入位置（放到依赖项的后面）
        依赖项必须已经注册，否则无法计算位置
        """
        # 校验依赖都已注册
        for dep in deps:
            if dep not in cls._registry_value:
                raise LibraryError(
                    f"{cls.name} require register {dep} before register {key}."
                )

        cls._registry_deps[key] = set(deps)

        items = list(cls._registry_value.items())

        # 计算所有依赖的最大位置
        dep_indices = [i for i, (k, _) in enumerate(items) if k in deps]
        return max(dep_indices) + 1

    @classmethod
    @final
    def _with_order(cls, key: K, order: int) -> int:  # pragma: no cover
        """
        根据顺序定义，找到_registry_value的插入位置
        """
        # 插入到第一个 >= order的位置
        items = list(cls._registry_value.items())
        for insert_idx, (exist_key, _) in enumerate(items):
            exist_order = cls._registry_order.get(exist_key, -sys.maxsize)
            if order <= exist_order:
                break
        else:
            # 没有break
            insert_idx = len(items)

        cls._registry_order[key] = order

        return insert_idx

    @classmethod
    @final
    def _compute_order_on_register(
        cls, func_or_obj: V, key: K, order, deps, meta
    ) -> None:  # pragma: no cover
        """
        在register时就计算顺序，有问题
        1. 不支持同时存在order和deps
        2. 使用deps，即依赖声明时，依赖项不存在，无法计算顺序
        """
        if order is not None and deps is not None:
            raise LibraryError(
                f"{cls.name} key {key} order or deps, cannot set together."
            )
        v = Entry(func_or_obj, meta)
        if key in cls._registry_value:
            cls._registry_value[key] = v
            return

        if deps is not None:
            insert_idx = cls._with_deps(key, deps)
        elif order is not None:
            insert_idx = cls._with_order(key, order)
        else:
            insert_idx = 0

        items = list(cls._registry_value.items())
        items.insert(insert_idx, (key, v))
        cls._registry_value = OrderedDict(items)
        return

    @classmethod
    @final
    def _compute_order_on_all(cls, func_or_obj: V, key: K, order, deps, meta) -> None:
        """
        调用all时计算顺序
        """
        cls._registry_value[key] = Entry(func_or_obj, meta)
        if order is not None:
            cls._registry_order[key] = order
        else:
            # 如果没有order，按插入顺序排列
            cls._registry_order[key] = len(cls._registry_value)

        if deps:
            cls._registry_deps[key].update(deps)
        else:
            cls._registry_deps[key] = set()
        cls._sorted_keys = None  # 注册新组件时重置缓存

    @classmethod
    @final
    def _compute_order(cls) -> None:
        if cls._sorted_keys is not None:
            return

        # 全局拓扑排序，order和依赖都考虑
        keys = cls._registry_value.keys()
        graph = defaultdict(set)  # 依赖项指向节点，后续需先处理完依赖项，再处理节点
        in_degree = {k: 0 for k in keys}  # 入度和依赖项挂钩，即k的依赖数量
        default_order = 0

        # deps，依赖边
        for key, deps in cls._registry_deps.items():
            for dep in deps:
                if dep not in cls._registry_value:
                    raise LibraryUsageError(
                        f"{cls.name} require register {dep} for register {key}."
                    )
                graph[dep].add(key)
                in_degree[key] += 1

        # order，依赖边，order大的依赖order小的
        for ki in keys:
            oi = cls._registry_order.get(ki, default_order)
            for kj in keys:
                if ki == kj:
                    continue
                oj = cls._registry_order.get(kj, default_order)
                if oi < oj:
                    # oj依赖于oi
                    if kj not in graph[ki]:
                        graph[ki].add(kj)
                        in_degree[kj] += 1

        # 拓扑排序（Kahn算法）
        # 先处理没有依赖的
        queue = deque([k for k in keys if in_degree[k] == 0])
        result: List[K] = []
        while queue:
            key = queue.popleft()  # 包括原来都没有的，以及已处理完所有依赖项的k
            result.append(key)
            for neighbor in graph[key]:  # 找到依赖node的节点
                in_degree[neighbor] -= 1  # 依赖node的节点依赖数减1
                if in_degree[neighbor] == 0:  # 依赖node的节点没有依赖项未处理了
                    queue.append(neighbor)
        if len(result) != len(keys):  # pragma: no cover # 屏蔽覆盖：正常不会发生
            raise LibraryUsageError(f"{cls.name} dependency/order conflicts or cycles")
        # 缓存排序结果
        cls._sorted_keys = tuple(result)

    @classmethod
    def register(
        cls,
        key: K,
        only_register_once: bool = True,
        order: Optional[int] = None,
        deps: Optional[Sequence[K]] = None,
        meta: Optional[MetaT] = None,
    ) -> Callable[[V], V]:
        """
        order越大，生效顺序越靠后；
        注意：类装饰器的注册/副作用”只会在首次 import 时发生，之后重新实例化并不会自动重新注册
        一次调用里，order和deps不能同时指定；不同调用里，可以有order/deps
        Args:
            key (K): key类
            only_register_once (bool, optional): 只能注册一次. Defaults to True.
            order (int, optional): 生效顺序. Defaults to 0.
        """
        if only_register_once and key in cls._registry_value:
            raise LibraryError(f"{cls.name} key {key} already registered.")

        def decorator(func_or_obj: V):
            # cls._compute_order_on_register(func_or_obj, key, order, deps, meta)
            cls._compute_order_on_all(func_or_obj, key, order, deps, meta)
            return func_or_obj

        return decorator

    @classmethod
    def get_entry(cls, key: K) -> Entry:
        if key not in cls._registry_value:
            raise LibraryUsageError(f"{cls.name} key {key} not registered.")
        return cls._registry_value[key]

    @classmethod
    def get(cls, key: K) -> V:
        return cls.get_entry(key).v

    @classmethod
    def get_meta(cls, key: K, meta_cls: Type[MetaT]) -> MetaT:
        return cls.get_entry(key).meta or meta_cls()

    @classmethod
    @final
    def all_entries(cls) -> Iterator[tuple[K, Entry[V, MetaT]]]:
        cls._compute_order()
        if cls._sorted_keys is None:  # pragma: no cover # 屏蔽覆盖：正常不会发生
            raise LibraryError(f"{cls.name} _sorted_keys None!")

        return ((k, cls._registry_value[k]) for k in cls._sorted_keys)

    @classmethod
    @final
    def all(cls) -> Iterator[Tuple[K, V]]:
        return ((k, entry.v) for k, entry in cls.all_entries())
