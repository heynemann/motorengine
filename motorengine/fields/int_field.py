#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class IntField(BaseField):
    '''
    Field responsible for storing integer values (:py:func:`int`).

    Usage:

    .. testcode:: modeling_fields

        name = IntField(required=True, min_value=0, max_value=255)

    Available arguments (apart from those in `BaseField`):

    * `min_value` - Raises a validation error if the integer being stored is lesser than this value
    * `max_value` - Raises a validation error if the integer being stored is greather than this value
    '''

    def __init__(self, min_value=None, max_value=None, *args, **kw):
        super(IntField, self).__init__(*args, **kw)
        self.min_value = min_value
        self.max_value = max_value

    def to_son(self, value):
        if value is None:
            return None
        return int(value)

    def from_son(self, value):
        if value is None:
            return None
        return int(value)

    def validate(self, value):
        if value is None:
            return True
        try:
            value = int(value)
        except:
            return False

        if self.min_value is not None and value < self.min_value:
            return False

        if self.max_value is not None and value > self.max_value:
            return False

        return True
