#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.lesser_than import LesserThanQueryOperator
from tests import AsyncTestCase


class TestLesserThanQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = LesserThanQueryOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", 10)).to_be_like({
            "field_name": {
                "$lt": 10
            }
        })
