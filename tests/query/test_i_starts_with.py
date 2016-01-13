#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.i_starts_with import IStartsWithOperator
from tests import AsyncTestCase


class TestIStartsWithOperator(AsyncTestCase):
    def test_to_query(self):
        query = IStartsWithOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "bEr")).to_be_like({
            "field_name": {
                "$regex": "^bEr",
                "$options": 'i'
            }
        })
