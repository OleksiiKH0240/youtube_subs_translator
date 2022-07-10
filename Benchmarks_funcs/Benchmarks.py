import functools
import time
from typing import List


def benchmark(kwargs2show: List[str, ] = None):
    if kwargs2show is None:
        kwargs2show = []

    def _benchmark(func):
        @functools.wraps(func)
        def __benchmark(*args, **kwargs):
            t = time.time()
            res = func(*args, **kwargs)
            t1 = time.time() - t
            if kwargs2show and kwargs:
                showStr = "; ".join([f'{k}={v}' for k, v in kwargs.items() if k in kwargs2show])
                print(f'{func}, with keyword arguments: {showStr}, time elapsed:', t1)
            else:
                print(f'{func}, time elapsed:', t1)

            return res

        return __benchmark

    return _benchmark
