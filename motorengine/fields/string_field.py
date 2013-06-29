#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from motorengine.fields.base_field import BaseField


class StringField(BaseField):
    def __init__(self, max_length=None, *args, **kw):
        super(StringField, self).__init__(*args, **kw)
        self.max_length = max_length

    def validate(self, value):
        is_string = isinstance(value, six.string_types)

        if not is_string:
            return False

        below_max_length = self.max_length is not None and len(value) <= self.max_length

        return self.max_length is None or below_max_length

    def is_empty(self, value):
        return value is None or value == ""
