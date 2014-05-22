#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


try:
    from ujson import loads, dumps

    def serialize(value):
        return dumps(value)

    def deserialize(value):
        return loads(value)
except ImportError:
    from json import loads, dumps
    from bson import json_util

    def serialize(value):
        return dumps(value, default=json_util.default)

    def deserialize(value):
        return loads(value, object_hook=json_util.object_hook)


def get_class(module_name, klass=None):
    if '.' not in module_name and klass is None:
        raise ImportError("Can't find class %s." % module_name)

    try:
        module_parts = module_name.split('.')

        if klass is None:
            module_name = '.'.join(module_parts[:-1])
            klass_name = module_parts[-1]
        else:
            klass_name = klass

        module = __import__(module_name)

        if '.' in module_name:
            for part in module_name.split('.')[1:]:
                module = getattr(module, part)

        return getattr(module, klass_name)
    except AttributeError:
        err = sys.exc_info()
        raise ImportError("Can't find class %s (%s)." % (module_name, str(err)))
