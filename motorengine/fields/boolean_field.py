#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class BooleanField(BaseField):
    def __init__(self, *args, **kw):
        super(BooleanField, self).__init__(*args, **kw)

    def to_son(self, value):
        if bool(value):
            return 1
        return 0

    def from_son(self, value):
        return value == 1
