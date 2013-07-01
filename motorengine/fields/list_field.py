#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class ListField(BaseField):
    def __init__(self, field=None, *args, **kw):
        super(ListField, self).__init__(*args, **kw)

        if not isinstance(field, BaseField):
            raise ValueError("The list field 'field' argument must be an instance of BaseField, not '%s'." % str(field))

        if not self.default:
            self.default = []

        self._base_field = field

    def validate(self, value):
        for item in value:
            if not self._base_field.validate(item):
                return False

        return True

    def is_empty(self, value):
        return value is None or value == []

    def to_son(self, value):
        return map(self._base_field.to_son, value)

    def from_son(self, value):
        return map(self._base_field.from_son, value)
