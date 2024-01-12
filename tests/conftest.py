from functools import wraps
from typing import Callable
from typing import Literal
from typing import TypeAlias

import pytest


Scope: TypeAlias = Literal[
    'function',
    'class',
    'module',
    'package',
    'session',
]


def dependency(depends: list[str] = list(), scope: Scope = 'session'):
    def get_func(func: Callable):
        @wraps(func)
        @pytest.mark.dependency(depends=depends, scope=scope)
        @pytest.mark.order(after=depends)
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return wrapper

    return get_func
