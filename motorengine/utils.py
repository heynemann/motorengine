#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys


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
