#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField

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


class JsonField(BaseField):
    '''
    Field responsible for storing json objects.

    Usage::

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
