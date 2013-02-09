import os
from .utils import is_root


def requires_root(command):
    def wrap(func):
        def inner(*args, **kwargs):
            if not is_root():
                return os.system(command.format(*args, **kwargs))
            else:
                return func(*args, **kwargs)
        return inner
    return wrap
