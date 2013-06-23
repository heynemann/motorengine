import six

import motorengine.document
from motorengine.document import *  # NOQA
import motorengine.fields
from motorengine.fields import *  # NOQA
import motorengine.connection
from motorengine.connection import *  # NOQA
import motorengine.queryset
from motorengine.queryset import *  # NOQA
import motorengine.signals
from motorengine.signals import *  # NOQA
from motorengine.errors import *  # NOQA
import motorengine.errors
import motorengine.django  # NOQA

__all__ = (list(document.__all__) + fields.__all__ + connection.__all__ +
           list(queryset.__all__) + signals.__all__ + list(errors.__all__))

VERSION = (0, 8, 2)


def get_version():
    if isinstance(VERSION[-1], six.string_types):
        return '.'.join(map(str, VERSION[:-1])) + VERSION[-1]
    return '.'.join(map(str, VERSION))

__version__ = get_version()
