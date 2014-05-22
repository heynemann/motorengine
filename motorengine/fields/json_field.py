#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField
from motorengine.utils import serialize, deserialize


class JsonField(BaseField):
    '''
    Field responsible for storing json objects.

    Usage:

    .. testcode:: modeling_fields

        name = JsonField(required=True)

    Available arguments (apart from those in `BaseField`): `None`

    .. note ::

        If ujson is available, MotorEngine will try to use it.
        Otherwise it will fallback to the json serializer that comes with python.
    '''

    def validate(self, value):
        try:
            serialize(value)
            return True
        except:
            return False

    def to_son(self, value):
        return serialize(value)

    def from_son(self, value):
        return deserialize(value)
