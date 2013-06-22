#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields import BaseField


class StringField(BaseField):
    def __init__(self, max_length=None, *args, **kw):
        super(StringField, self).__init__(*args, **kw)
        self.max_length = max_length
