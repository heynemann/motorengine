from tests.all_warnings import AllWarnings  # NOQA
from tests.document import *  # NOQA
from tests.queryset import *  # NOQA
from tests.fields import *  # NOQA
from tests.migration import *  # NOQA


def disabled(func):
    def wrapper(func):
        func.__test__ = False
        return func

    return wrapper
