#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.lesser_than_or_equal import LesserThanOrEqualQueryOperator
from tests import AsyncTestCase


class TestLesserThanOrEqualQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = LesserThanOrEqualQueryOperator(10)
        expect(query).not_to_be_null()
        expect(query.to_query()).to_be_like({
            "$lte": 10
        })
