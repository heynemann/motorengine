#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class BooleanField(BaseField):
    def __init__(self, *args, **kw):
        super(BooleanField, self).__init__(*args, **kw)

    def to_son(self, value):
        return bool(value)

    def from_son(self, value):
        return value
