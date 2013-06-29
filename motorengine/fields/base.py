#!/usr/bin/env python
# -*- coding: utf-8 -*-


class BaseField(object):
    total_creation_counter = 0

    def __init__(self, db_field=None, default=None, required=False):
        global creation_counter
        self.creation_counter = BaseField.total_creation_counter
        BaseField.total_creation_counter += 1

        self.db_field = db_field
        self.required = required
        self.default = default

    def is_empty(self, value):
        return value is None

    def to_son(self, value):
        return value

    def from_son(self, value):
        return value

    def validate(self, value):
        return True
