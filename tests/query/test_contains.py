#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.contains import ContainsOperator
from tests import AsyncTestCase


class TestContainsOperator(AsyncTestCase):
    def test_to_query(self):
        query = ContainsOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "nar")).to_be_like({
            "field_name": {
                "$regex": "nar"
            }
        })
