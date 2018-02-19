#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.i_exact import IExactOperator
from tests import AsyncTestCase


class TestIExactOperator(AsyncTestCase):
    def test_to_query(self):
        query = IExactOperator()
        expect(query).not_to_be_null()
        expect(query.to_query("field_name", "bErNaRdO")).to_be_like({
            "field_name": {
                "$regex": "^bErNaRdO$",
                "$options": 'i'
            }
        })
