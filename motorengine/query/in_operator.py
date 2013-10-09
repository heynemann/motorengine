#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class InQueryOperator(QueryOperator):
    def to_query(self, field_name, value):
        return {
            field_name: {
                "$in": value
            }
        }

    def get_value(self, field, value):
        return [field.to_son(val) for val in value]
