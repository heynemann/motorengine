#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField
from motorengine.utils import serialize, deserialize


class DynamicField(BaseField):
    '''
    Field responsible for storing dynamic arguments.
    '''

    @property
    def name(self):
        return self.db_field.replace('dynamic_field_', '')

    def from_son(self, value):
        return deserialize(value)

    def to_son(self, value):
        return serialize(value)
