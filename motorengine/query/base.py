#!/usr/bin/env python
# -*- coding: utf-8 -*-


class QueryOperator(object):
    def get_value(self, field, raw_value):
        return field.to_son(raw_value)

    def to_query(self, value):
        raise NotImplementedError()
