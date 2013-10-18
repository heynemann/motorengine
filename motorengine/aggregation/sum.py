#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.aggregation.base import BaseAggregation


class SumAggregation(BaseAggregation):
    def to_query(self, aggregation):
        alias = self.alias
        field_name = aggregation.get_field_name(self.field)

        if alias is None:
            alias = field_name

        return {
            alias: {"$sum": ("$%s" % field_name)}
        }
