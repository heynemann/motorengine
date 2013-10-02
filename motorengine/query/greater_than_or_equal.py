#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class GreaterThanOrEqualQueryOperator(QueryOperator):
    def to_query(self):
        return {"$gte": self.value}
