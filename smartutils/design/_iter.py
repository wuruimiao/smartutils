from typing import Any, Callable, Generator, Tuple


def drive_steps(gen: Generator[Tuple[Callable[..., Any], dict], Any, Any]) -> Any:
    try:
        op = next(gen)  # 激活生成器，获得第一个操作步骤
        while True:
            func, kwargs = op
            result = func(**kwargs)  # 执行具体的同步方法
            op = gen.send(result)  # send 上一步的结果回去，主逻辑流程内部判断
    except StopIteration as e:
        return e.value


async def adrive_steps(
    gen: Generator[Tuple[Callable[..., Any], dict], Any, Any],
) -> Any:
    try:
        op = next(gen)  # 激活生成器，获得第一个操作步骤
        while True:
            func, kwargs = op
            result = await func(**kwargs)  # 执行具体的同步方法
            op = gen.send(result)  # send 上一步的结果回去，主逻辑流程内部判断
    except StopIteration as e:
        return e.value
