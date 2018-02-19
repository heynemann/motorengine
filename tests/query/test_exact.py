#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.exact import ExactOperator
from tests import AsyncTestCase


class TestExactOperator(AsyncTestCase):
    def test_to_query(self):
        query = ExactOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "Bernardo")).to_be_like({
            "field_name": {
                "$regex": "^Bernardo$"
            }
        })
