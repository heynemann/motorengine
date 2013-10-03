#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine.query.is_null import IsNullQueryOperator
from tests import AsyncTestCase


class TestExistsQueryOperator(AsyncTestCase):
    def test_to_query(self):
        query = IsNullQueryOperator()
        expect(query).not_to_be_null()

        expect(query.to_query("field_name", True)).to_be_like({
            "field_name": None
        })

        expect(query.to_query("field_name", False)).to_be_like({
            "field_name": {
                "$exists": True,
                "$ne": None
            }
        })
