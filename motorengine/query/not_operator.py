#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class NotOperator(QueryOperator):
    def to_query(self, field_name, operator, value):
        result = operator.to_query(field_name, value)

        return {
            field_name: {
                "$not": result[field_name]
            }
        }

    def get_value(self, field, value):
        return value
