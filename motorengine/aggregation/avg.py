#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.aggregation.base import BaseAggregation


class AverageAggregation(BaseAggregation):
    def to_query(self, queryset):
        alias = self.alias
        if alias is None:
            alias = self.field.db_field

        return {
            self.field.db_field: {"$avg": ("$%s" % self.field.db_field)}
        }
