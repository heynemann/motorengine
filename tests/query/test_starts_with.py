#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.starts_with import StartsWithOperator
from tests import AsyncTestCase


class TestStartsWithOperator(AsyncTestCase):
    def test_to_query(self):
        query = StartsWithOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "^Ber")).to_be_like({
            "field_name": {
                "$regex": "^Ber"
            }
        })
