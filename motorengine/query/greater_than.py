#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class GreaterThanQueryOperator(QueryOperator):
    def to_query(self):
        return {"$gt": self.value}
