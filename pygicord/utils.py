import asyncio

from typing import Any, Callable
from functools import wraps

__all__ = ("ensure_coroutine",)


def ensure_coroutine(func: Callable[..., Any]) -> Callable[..., Any]:
    if asyncio.iscoroutinefunction(func):
        return func
    else:

        @wraps(func)
        async def coro(*args, **kwargs):
            return func(*args, **kwargs)

        return coro
