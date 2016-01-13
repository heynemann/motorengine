#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.i_ends_with import IEndsWithOperator
from tests import AsyncTestCase


class TestIEndsWithOperator(AsyncTestCase):
    def test_to_query(self):
        query = IEndsWithOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "Do")).to_be_like({
            "field_name": {
                "$regex": "Do$",
                "$options": 'i'
            }
        })
