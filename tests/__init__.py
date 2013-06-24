from tornado.testing import AsyncTestCase as TornadoAsyncTestCase


def disabled(func):
    def wrapper(func):
        func.__test__ = False
        return func

    return wrapper


class AsyncTestCase(TornadoAsyncTestCase):
    def stop(self, *args, **kwargs):
        """Stops the `.IOLoop`, causing one pending (or future) call to `wait()`
        to return.

        Keyword arguments or a single positional argument passed to `stop()` are
        saved and will be returned by `wait()`.
        """
        self.__stop_args = {
            'args': args,
            'kwargs': kwargs
        }
        if self.__running:
            self.io_loop.stop()
            self.__running = False
        self.__stopped = True


# MUST BE AFTER DECLARING AsyncTestCase
from tests.all_warnings import AllWarnings  # NOQA
from tests.document import *  # NOQA
from tests.queryset import *  # NOQA
from tests.fields import *  # NOQA
from tests.migration import *  # NOQA
