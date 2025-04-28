import inspect


async def call_hook(hook, *args, **kwargs):
    if hook is None:
        return

    result = hook(*args, **kwargs)
    if inspect.isawaitable(result):
        await result
