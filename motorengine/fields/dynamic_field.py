#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class DynamicField(BaseField):
    '''
    Field responsible for storing dynamic arguments.
    '''

    @property
    def name(self):
        return self.db_field.lstrip('_')

    def to_query(self, value):
        if isinstance(value, (tuple, set, list)):
            return {
                "$all": value
            }

        return value
