#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.ends_with import EndsWithOperator
from tests import AsyncTestCase


class TestEndsWithOperator(AsyncTestCase):
    def test_to_query(self):
        query = EndsWithOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "do$")).to_be_like({
            "field_name": {
                "$regex": "do$"
            }
        })
