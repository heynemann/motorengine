#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.greater_than_or_equal import GreaterThanOrEqualQueryOperator
from tests import AsyncTestCase


class TestGreaterThanOrEqualQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = GreaterThanOrEqualQueryOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", 10)).to_be_like({
            "field_name": {
                "$gte": 10
            }
        })
