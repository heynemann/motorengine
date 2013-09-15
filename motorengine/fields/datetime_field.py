#!/usr/bin/env python
# -*- coding: utf-8 -*-

import six

from datetime import datetime

from motorengine.fields.base_field import BaseField

FORMAT = "%Y-%m-%d %H:%M:%S"


class DateTimeField(BaseField):
    def __init__(self, *args, **kw):
        super(DateTimeField, self).__init__(*args, **kw)

    def to_son(self, value):
        if value is None:
            return None

        if isinstance(value, six.string_types):
            return datetime.strptime(value, FORMAT)

        return value

    def from_son(self, value):
        if isinstance(value, datetime):
            return value

        return datetime.strptime(value, FORMAT)

    def validate(self, value):
        return isinstance(value, datetime)
