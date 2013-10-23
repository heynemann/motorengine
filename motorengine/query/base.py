#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.fields.base_field import BaseField


class QueryOperator(object):
    def get_value(self, field, raw_value):
        if field is None or not isinstance(field, (BaseField, )):
            return raw_value

        return field.to_query(raw_value)

    def to_query(self, value):
        raise NotImplementedError()
