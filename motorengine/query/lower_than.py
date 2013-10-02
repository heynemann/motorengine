#!/usr/bin/env python
# -*- coding: utf-8 -*-

from motorengine.query.base import QueryOperator


class LowerThanQueryOperator(QueryOperator):
    def to_query(self):
        return {"$lt": self.value}
