from threading import Thread
from typing import Any


class ThreadWithReturnValue(Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs: dict | None = None, Verbose=None):
        super().__init__(self, group, target, name, args, kwargs)
        if kwargs is None:
            kwargs = {}
        self._args = args
        self._target = target
        self._kwargs = kwargs
        self._return = None

    def run(self):
        if self._target:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args) -> Any:
        Thread.join(self, *args)
        return self._return