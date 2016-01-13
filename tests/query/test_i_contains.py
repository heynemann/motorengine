#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.i_contains import IContainsOperator
from tests import AsyncTestCase


class TestIContainsOperator(AsyncTestCase):
    def test_to_query(self):
        query = IContainsOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "NaR")).to_be_like({
            "field_name": {
                "$regex": "NaR",
                "$options": 'i'
            }
        })
