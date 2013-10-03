#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class ExistsQueryOperator(QueryOperator):
    def to_query(self, field_name, value):
        return {
            field_name: {
                "$exists": value,
                "$ne": None
            }
        }

    def get_value(self, field, value):
        return value
