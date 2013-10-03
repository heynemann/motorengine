#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class LesserThanOrEqualQueryOperator(QueryOperator):
    def to_query(self, field_name, value):
        return {
            field_name: {"$lte": value}
        }
