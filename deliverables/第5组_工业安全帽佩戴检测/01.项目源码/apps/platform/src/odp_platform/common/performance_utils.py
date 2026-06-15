import time
import functools
import logging
from typing import Callable

logger = logging.getLogger("odp_platform.performance")

def time_it(func: Callable = None, *, label: str = None):
    """装饰器，记录函数执行耗时。label 为空时用 func.__name__。"""
    def decorator(f: Callable):
        name = label or f.__name__
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                logger.debug(f"{name} 耗时: {elapsed:.4f}s")
        return wrapper
    if func is not None:
        return decorator(func)
    return decorator
