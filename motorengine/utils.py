#!/usr/bin/env python
# -*- coding: utf-8 -*-


def get_class(module_name, klass):
    module = __import__(module_name)
    if '.' in module_name:
        module = reduce(getattr, module_name.split('.')[1:], module)

    return getattr(module, klass)
