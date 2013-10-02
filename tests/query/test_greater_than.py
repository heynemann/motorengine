#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.greater_than import GreaterThanQueryOperator
from tests import AsyncTestCase


class TestGreaterThanQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = GreaterThanQueryOperator(10)
        expect(query).not_to_be_null()
        expect(query.to_query()).to_be_like({
            "$gt": 10
        })
