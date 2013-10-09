#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.not_equal import NotEqualQueryOperator
from tests import AsyncTestCase


class TestNotEqualQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = NotEqualQueryOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", 10)).to_be_like({
            "field_name": {
                "$ne": 10
            }
        })
