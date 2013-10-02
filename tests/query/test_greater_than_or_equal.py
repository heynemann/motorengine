#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.greater_than_or_equal import GreaterThanOrEqualQueryOperator
from tests import AsyncTestCase


class TestGreaterThanOrEqualQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = GreaterThanOrEqualQueryOperator(10)
        expect(query).not_to_be_null()
        expect(query.to_query()).to_be_like({
            "$gte": 10
        })
