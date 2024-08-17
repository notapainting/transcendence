import asyncio, time


class BaseTimer:
    _start = None
    _middle = None
    _end = None
    _pause = True
    _e = 3

    def __init__(self, verbose=False, e=3) -> None:
        self.verbose = verbose
        self._e = e

    def time(self):
        return time.time()

    def paused(self):
        return self._pause

    def epsilon(self):
        return self._e


class SnipTimer(BaseTimer):
    _startns = None
    _middlens = None
    _endns = None

    def __enter__(self):
        self._start = time.perf_counter()
        self._startns = time.process_time()
        if self.verbose is True:
            print(f"snip: start: {self._start:.{self._e}f}")

    def __exit__(self):
        self._end = time.perf_counter()
        self._endns = time.process_time()
        self._elapsed = self._end - self._start
        self._elapsedns = self._endns - self._startns
        if self.verbose is True:
            print(f"snip: end")
            if self._elapsed == self._elapsedns:
                print(f"snip: elapsed time : {self._elapsed:.{self._e}f}")
            else:
                print(f"snip: elapsed time : {self._elapsed:.{self._e}f}, ns: {self._elapsedns:.{self._e}f}")


class Timer(BaseTimer):
    def get_running_time(self):
        if self._start is None:
            value = 0.0
        elif self._pause is True:
            value = self._middle - self._start
        else:
            value = time.time() - self._start
        if self.verbose is True:
            print(f"timer: {value:.{self._e}f}")
        return value

    def resume(self):
        if self._start is None:
            self._start = time.time()
            self._pause = False
            if self.verbose is True:
                print(f"timer: start")
        else:
            if self._pause is True:
                self._start += (time.time() - self._middle)
                self._pause = False
        return self.paused()

    def pause(self):
        if self._pause is False:
            self._middle = time.time()
            self._pause = True
            if self.verbose is True:
                self.get_running_time()
        return self.paused()

    def restart(self):
        self._pause = False
        self._middle = None
        self._start = time.time()
        if self.verbose is True:
                print(f"timer: restart")

    def reset(self):
        self._pause = True
        self._middle = None
        self._start = None
        if self.verbose is True:
                print(f"timer: reset")

class ATimer(BaseTimer):
    _loop = None

    def __init__(self, verbose=False, e=3) -> None:
        super().__init__(verbose, e)
        self._loop = asyncio.get_event_loop()

    def time(self):
        return self._loop.time()

    def get_running_time(self):
        if self._start is None:
            value = 0.0
        elif self._pause is True:
            value = self._middle - self._start
        else:
            value = self._loop.time() - self._start
        if self.verbose is True:
            print(f"timer: {value:.{self._e}f}")
        return value

    def resume(self):
        if self._start is None:
            self._start = self._loop.time()
            self._pause = False
            if self.verbose is True:
                print(f"atimer: start")
        else:
            if self._pause is True:
                self._start += (self._loop.time() - self._middle)
                self._pause = False
        return self.paused()

    def pause(self):
        if self._pause is False:
            self._middle = self._loop.time()
            self._pause = True
            if self.verbose is True:
                self.get_running_time()
        return self.paused()

    def restart(self):
        self._pause = False
        self._middle = None
        self._start = self._loop.time()
        if self.verbose is True:
                print(f"atimer: restart")

    def reset(self):
        self._pause = True
        self._middle = None
        self._start = None
        if self.verbose is True:
                print(f"atimer: reset")
