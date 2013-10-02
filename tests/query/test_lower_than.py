#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.lower_than import LowerThanQueryOperator
from tests import AsyncTestCase


class TestLowerThanQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = LowerThanQueryOperator(10)
        expect(query).not_to_be_null()
        expect(query.to_query()).to_be_like({
            "$lt": 10
        })
