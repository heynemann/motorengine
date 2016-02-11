#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class BooleanField(BaseField):
    '''
    Field responsible for storing boolean values (:py:func:`bool`).

    Usage:

    .. testcode:: modeling_fields

        isActive = BooleanField(required=True)

    `BooleanField` has no additional arguments available (apart from those in `BaseField`).
    '''
    def __init__(self, *args, **kw):
        super(BooleanField, self).__init__(*args, **kw)

    def to_son(self, value):
        return bool(value)

    def from_son(self, value):
        return value
