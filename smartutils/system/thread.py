import threading


def is_main_thread() -> bool:
    """
    是否是主线程，可用于判读是否是多线程环境
    """
    return threading.current_thread() == threading.main_thread()


def is_multithreaded() -> bool:
    """
    是否有子线程（多线程），可用于判断是否是多线程环境
    """
    return threading.active_count() > 1
