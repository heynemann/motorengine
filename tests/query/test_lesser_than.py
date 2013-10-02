#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.lesser_than import LesserThanQueryOperator
from tests import AsyncTestCase


class TestLesserThanQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = LesserThanQueryOperator(10)
        expect(query).not_to_be_null()
        expect(query.to_query()).to_be_like({
            "$lt": 10
        })
