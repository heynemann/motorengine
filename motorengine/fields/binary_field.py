#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.fields.base_field import BaseField


class BinaryField(BaseField):
    '''
    Field responsible for storing binary values.

    Usage:

    .. testcode:: modeling_fields

        name = BinaryField(required=True)

    Available arguments (apart from those in `BaseField`):

    * `max_bytes` - The maximum number of bytes that can be stored in this field
    '''

    def __init__(self, max_bytes=None, *args, **kwargs):
        super(BinaryField, self).__init__(*args, **kwargs)
        self.max_bytes = max_bytes

    def to_son(self, value):
        if not isinstance(value, (six.binary_type, )):
            return six.b(value)

        return value

    def from_son(self, value):
        if not isinstance(value, (six.binary_type, )):
            return six.b(value)

        return value

    def validate(self, value):
        if not isinstance(value, (six.binary_type, )):
            return False

        if self.max_bytes is not None and len(value) > self.max_bytes:
            return False

        return True

    def is_empty(self, value):
        return value is None or value == ""
