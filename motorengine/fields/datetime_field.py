#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

from motorengine.fields.base_field import BaseField

FORMAT = "%Y-%m-%d-%H-%M-%S"


class DateTimeField(BaseField):
    def __init__(self, *args, **kw):
        super(DateTimeField, self).__init__(*args, **kw)

    def to_son(self, value):
        return value.strftime(FORMAT)

    def from_son(self, value):
        if isinstance(value, datetime):
            return value

        return datetime.strptime(value, FORMAT)

    def validate(self, value):
        return isinstance(value, datetime)
