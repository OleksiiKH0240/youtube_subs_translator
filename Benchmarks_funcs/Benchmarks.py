def benchmark(func):
    import time
    def _benchmark(*args, **kw):
        t = time.time()
        res = func(*args, **kw)
        print('time elapsed:', time.time()-t)
        return res
    return _benchmark
