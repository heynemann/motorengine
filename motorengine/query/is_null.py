#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class IsNullQueryOperator(QueryOperator):
    def to_query(self, field_name, value):
        if value:
            return {
                field_name: None
            }
        else:
            return {
                field_name: {
                    "$exists": True,
                    "$ne": None
                }
            }

    def get_value(self, field, value):
        return value
