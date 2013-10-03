#!/usr/bin/env python
# -*- coding: utf-8 -*-


from preggy import expect

from motorengine import StringField
from motorengine.query.base import QueryOperator
from tests import AsyncTestCase


class TestBaseQueryOperator(AsyncTestCase):
    def test_can_create_query_operator(self):
        query = QueryOperator()
        expect(query).not_to_be_null()
        expect(query.get_value(StringField(), "some value")).to_equal("some value")
